import json
import os
import base64
import requests
from typing import Optional
from pathlib import Path

class FineTuneClient:
    def __init__(self, api_key: str, host: str = "api.us1.bfl.ai"):
        self.api_key = api_key
        self.host = host
        
    def _encode_file(self, file_path: str) -> str:
        """Encode file to base64."""
        with open(file_path, 'rb') as f:
            file_data = f.read()
            return base64.b64encode(file_data).decode('utf-8')
    
    def start_finetune(
        self,
        file_path: str,
        model_name: str,
        trigger_word: str,
        mode: str = 'character',
        finetune_type: str = 'lora',
        iterations: int = 1000,
        lora_rank: Optional[int] = None,
        learning_rate: Optional[float] = None,
        priority: str = 'quality',
        auto_caption: bool = True
    ) -> dict:
        """Start a fine-tuning job."""
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            
            # Encode the file
            file_data = self._encode_file(file_path)
            
            # Prepare payload
            payload = {
                "file_data": file_data,
                "finetune_comment": model_name,
                "mode": mode,
                "trigger_word": trigger_word,
                "iterations": iterations,
                "captioning": auto_caption,
                "priority": priority,
                "finetune_type": finetune_type
            }
            
            # Add optional parameters
            if finetune_type == "lora" and lora_rank is not None:
                payload["lora_rank"] = lora_rank
            
            if learning_rate is not None:
                payload["learning_rate"] = learning_rate
            
            # Make API request
            url = f"https://{self.host}/v1/finetune"
            headers = {
                "Content-Type": "application/json",
                "X-Key": self.api_key
            }
            
            print(f"\nStarting fine-tune for model: {model_name}")
            print(f"Parameters:")
            print(f"- Mode: {mode}")
            print(f"- Type: {finetune_type}")
            print(f"- Iterations: {iterations}")
            if lora_rank:
                print(f"- LoRA Rank: {lora_rank}")
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Save job info
            if 'finetune_id' in result:
                job_info = {
                    'finetune_id': result['finetune_id'],
                    'model_name': model_name,
                    'trigger_word': trigger_word,
                    'mode': mode,
                    'type': finetune_type,
                    'rank': lora_rank,
                    'iterations': iterations,
                    'learning_rate': learning_rate,
                    'priority': priority
                }
                
                # Save to file
                job_file = Path('latest_finetune.json')
                with open(job_file, 'w') as f:
                    json.dump(job_info, f, indent=2)
                print(f"\nSaved job info to {job_file}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error starting fine-tune: {e}")
            raise
    
    def check_status(self, finetune_id: str) -> dict:
        """Check the status of a fine-tuning job."""
        try:
            url = f"https://{self.host}/v1/finetune_details"
            headers = {"X-Key": self.api_key}
            params = {"finetune_id": finetune_id}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def list_finetunes(self) -> dict:
        """List all fine-tunes."""
        try:
            url = f"https://{self.host}/v1/my_finetunes"
            headers = {"X-Key": self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error listing fine-tunes: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

# Example usage
if __name__ == "__main__":
    # Your API key
    API_KEY = "21006105-1bcc-4969-abab-97e55051d7a3"
    
    # Initialize client
    client = FineTuneClient(api_key=API_KEY)
    
    # Example fine-tuning job
    try:
        result = client.start_finetune(
            file_path="paresh.zip",
            model_name="pareshranaut-character-lora-16",
            trigger_word="pareshranaut",
            mode="character",
            finetune_type="lora",
            iterations=1000,
            lora_rank=16,
            priority="quality",
            auto_caption=True
        )
        print("\nFine-tuning job started successfully:")
        print(json.dumps(result, indent=2))
        
        # Store the response for tracking
        with open('finetune_response.json', 'w') as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        print(f"\nError running fine-tuning: {e}")
        if isinstance(e, FileNotFoundError):
            print("\nPlease check that your ZIP file exists at the specified path and is properly zipped.") 