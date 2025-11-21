
from transformers.loss.loss_utils import ForCausalLMLoss
import torch
import torch.nn.functional as F

def loss_func(logits: torch.Tensor, labels: torch.LongTensor, vocab_size:int) -> torch.Tensor:
    IGNORE_INDEX = -100
    
    labels = F.pad(labels, [0,1], value=IGNORE_INDEX)
    shift_labels = labels[..., 1:].contiguous()

    # reshape
    logits = logits.view(-1, vocab_size)
    shift_labels = shift_labels.view(-1)

    loss = F.cross_entropy(logits, shift_labels, ignore_index=IGNORE_INDEX, reduction="mean")
    return loss

def test():
    batch = 4
    token_size = 8192
    vocab_size = 1300
    
    logits = torch.rand([batch, token_size, vocab_size], device='cuda')
    labels = torch.rand([batch, token_size], device='cuda')
    labels = (labels * vocab_size).to(torch.int64)

    gt = ForCausalLMLoss(logits, labels, vocab_size=vocab_size)

    dt = loss_func(logits, labels, vocab_size)
    assert torch.allclose(gt, dt)

if __name__ == '__main__':
    torch.manual_seed(42)
    test()
