"""
🤖 MULTI-AI CLIENT
═══════════════════════════════════════════════════════════════
Intelligent AI client that tries multiple models with fallback.
"""

import time
import requests
from typing import Optional, List, Dict, Tuple
from openai import OpenAI
import google.generativeai as genai

from ..config import OPENROUTER_API_KEY, GEMINI_API_KEY, YOUR_SITE_URL, YOUR_SITE_NAME, HEALTH_CHECK_DELAY, RETRY_DELAY
from .model_config import AI_MODELS
from .health_tracker import ModelHealthTracker


class MultiAIClient:
    """
    Intelligent AI client that tries multiple models with fallback.
    """
    
    def __init__(self):
        self.tracker = ModelHealthTracker()
        self.openrouter_client = None
        
        # Initialize OpenRouter client
        if OPENROUTER_API_KEY and "YOUR_" not in OPENROUTER_API_KEY:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
    
    def health_check_all_models(self):
        """
        Test all models with a simple prompt to see which are working.
        This runs at startup.
        """
        print("\nRunning health check on all AI models...")
        print("   (This takes ~30 seconds but ensures reliability)")
        
        test_prompt = "Respond with exactly: OK"
        
        for model_name, model_info in AI_MODELS.items():
            try:
                print(f"   Testing {model_name}...", end=" ")
                
                start_time = time.time()
                response = self._call_single_model(
                    model_name=model_name,
                    prompt=test_prompt,
                    max_tokens=50,
                    temperature=0.1
                )
                response_time = time.time() - start_time
                
                if response and len(response) > 0:
                    self.tracker.mark_success(model_name, response_time)
                    print(f"OK ({response_time:.2f}s)")
                else:
                    self.tracker.mark_failure(model_name, "Empty response")
                    print(f"FAILED (empty response)")
                    
            except Exception as e:
                self.tracker.mark_failure(model_name, str(e))
                print(f"FAILED ({str(e)[:50]})")
            
            # Rate limiting
            time.sleep(HEALTH_CHECK_DELAY)
        
        # Print summary
        print(self.tracker.get_status_report())
        
        healthy = self.tracker.get_healthy_models()
        if not healthy:
            print("WARNING: NO MODELS ARE WORKING!")
            print("   Please check your API keys and try again.")
            return False
        
        print(f"SUCCESS: {len(healthy)}/{len(AI_MODELS)} models are healthy and ready!")
        return True
    
    def _call_single_model(self, model_name: str, prompt: str, 
                          max_tokens: int = 600, temperature: float = 0.8) -> Optional[str]:
        """
        Call a single AI model.
        """
        model_info = AI_MODELS[model_name]
        
        if model_info["provider"] == "openrouter":
            return self._call_openrouter(model_info["id"], prompt, max_tokens, temperature)
        elif model_info["provider"] == "gemini_direct":
            return self._call_gemini_direct(prompt, max_tokens, temperature)
        
        return None
    
    def _call_openrouter(self, model_id: str, prompt: str, 
                        max_tokens: int, temperature: float) -> Optional[str]:
        """Call model via OpenRouter."""
        
        if not self.openrouter_client:
            raise Exception("OpenRouter client not initialized")
        
        completion = self.openrouter_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model=model_id,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return completion.choices[0].message.content
    
    def _call_gemini_direct(self, prompt: str, max_tokens: int, 
                           temperature: float) -> Optional[str]:
        """Call Gemini directly using Google Generative AI library."""
        
        if "YOUR_" in GEMINI_API_KEY:
            raise Exception("Gemini API key not configured")
        
        # Configure the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create the model
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        return response.text
    
    def generate_with_fallback(self, prompt: str, task_type: str = "creative_writing",
                              max_tokens: int = 600, temperature: float = 0.8,
                              max_attempts_per_model: int = 2) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate text using the best available model with automatic fallback.
        
        Returns: (generated_text, model_used)
        """
        
        # Step 1: Get models best suited for this task
        suitable_models = self._get_suitable_models(task_type)
        
        if not suitable_models:
            print("❌ No suitable models available!")
            return None, None
        
        # Step 2: Try each model in order
        for model_name in suitable_models:
            model_info = AI_MODELS[model_name]
            
            for attempt in range(1, max_attempts_per_model + 1):
                try:
                    print(f"   🤖 Trying {model_name} (attempt {attempt}/{max_attempts_per_model})...")
                    
                    start_time = time.time()
                    result = self._call_single_model(
                        model_name=model_name,
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    response_time = time.time() - start_time
                    
                    if result and len(result) > 50:  # Minimum viable response
                        self.tracker.mark_success(model_name, response_time)
                        print(f"   ✅ Success with {model_name}! ({response_time:.2f}s)")
                        return result, model_name
                    else:
                        print(f"   ⚠️  Response too short, retrying...")
                        
                except Exception as e:
                    self.tracker.mark_failure(model_name, str(e))
                    print(f"   ❌ Failed: {str(e)[:100]}")
                
                # Wait before retry
                if attempt < max_attempts_per_model:
                    time.sleep(RETRY_DELAY)
        
        # All models failed
        print("   ❌ ALL MODELS FAILED!")
        return None, None
    
    def _get_suitable_models(self, task_type: str) -> List[str]:
        """
        Get models suitable for the task, ordered by priority.
        """
        scored_models = []
        
        for model_name, model_info in AI_MODELS.items():
            # Skip if known to be unhealthy
            if self.tracker.health_status[model_name]["is_healthy"] == False:
                if self.tracker.health_status[model_name]["consecutive_failures"] >= 2:
                    continue
            
            # Calculate suitability score
            score = 0
            
            # Task-specific bonus
            if task_type in model_info["best_for"]:
                score += 30
            
            # Tier bonus (Tier 1 = best)
            score += (4 - model_info["tier"]) * 20
            
            # Health bonus
            status = self.tracker.health_status[model_name]
            if status["is_healthy"] == True:
                score += 25
            elif status["is_healthy"] == None:
                score += 10  # Untested models get medium priority
            
            # Success rate bonus
            if status["total_calls"] > 0:
                success_rate = status["total_successes"] / status["total_calls"]
                score += success_rate * 15
            
            # Speed bonus (slight preference for faster models)
            speed_map = {"very_fast": 5, "fast": 3, "medium": 1, "slow": 0}
            score += speed_map.get(model_info["speed"], 0)
            
            scored_models.append((model_name, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, score in scored_models]
