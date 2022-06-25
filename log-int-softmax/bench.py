import torch

def int_softmax(x, scaling_factor):

    def int_polynomial(x_int, scaling_factor):
        coef = [0.35815147, 0.96963238, 1.]  # ax**2 + bx + c
        coef[1] /= coef[0]
        coef[2] /= coef[0]
        b_int = torch.floor(coef[1] / scaling_factor)
        c_int = torch.floor(coef[2] / scaling_factor**2)
        z = x_int + b_int
        z = x_int * z
        z = z + c_int
        scaling_factor = coef[0] * scaling_factor**2
        return z, scaling_factor

    def int_exp(x_int, scaling_factor):
        x0 = -0.6931  # -ln2
        n = 30  # sufficiently large integer
        x0_int = torch.floor(x0 / scaling_factor)
        x_int = torch.max(x_int, n * x0_int)
        q = torch.floor(x_int / x0_int)
        r = x_int - x0_int * q
        exp_int, exp_scaling_factor = int_polynomial(r, scaling_factor)
        exp_int = torch.clamp(torch.floor(exp_int * 2**(n - q)), min=0)
        scaling_factor = exp_scaling_factor / 2**n
        return exp_int, scaling_factor

    x_int = x
    x_int_max, _ = x_int.max(dim=-1, keepdim=True)
    x_int = x_int - x_int_max
    exp_int, exp_scaling_factor = int_exp(x_int, scaling_factor)
    exp_int_sum = exp_int.sum(dim=-1, keepdim=True)
    return exp_int, exp_int_sum

def log_round(x):
    x_log_floor = x.log2().floor()
    big = x_log_floor
    extra_mask = (x - 2**big) >= 2**(big - 1)
    big[extra_mask] = big[extra_mask] + 1
    return big

def forward(x, scale):
    exp_int, exp_int_sum = int_softmax(x, scale)
    softmax_out = torch.round(exp_int_sum / exp_int)
    rounds = log_round(softmax_out)
    mask = rounds >= 16
    qlog = torch.clamp(rounds, 0, 15)
    qlog[mask] = -1
    
    return qlog
    
    
if __name__ == "__main__":
    import os

    # with open('lis_1174') as f:
    #     scale = float(f.readline())
    #     ll = f.readline().split(',')
    #     inp = [ float(val) for val in ll[0:len(ll)-1]]
    #     inp = torch.tensor(inp).round()
        
    #     ll = f.readline().split(',')
    #     DT = torch.tensor([ float(val) for val in ll[0:len(ll)-1]])
    #     DT = torch.tensor(DT).round()
    #     GT = forward(inp, torch.tensor(scale))
    #     print((GT-DT).argmax())

                                
    for root, dirs, files in os.walk('./'):
        for name in files:
            if 'lis_' not in name:
                continue;
            with open(name) as f:
                print(name)
                scale = float(f.readline())
                ll = f.readline().split(',')
                inp = [ float(val) for val in ll[0:len(ll)-1]]
                inp = torch.tensor(inp).round()
                
                
                ll = f.readline().split(',')
                DT = torch.tensor([ float(val) for val in ll[0:len(ll)-1]])
                DT = torch.tensor(DT).round()
                
                GT = forward(inp, torch.tensor(scale))

                if not GT.equal(DT):
                    print(name)
                    import sys
                    sys.exit(0)
                f.close()
                                