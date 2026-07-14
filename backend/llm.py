from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class LLMGenerator:
    def __init__(self, model_name: str = "google/flan-t5-large"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def generate(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Generate answer from prompt using the Seq2Seq model directly."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3
        )
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip()