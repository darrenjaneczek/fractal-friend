
from fractalfriend.interpolation import interpolate
from fractalfriend.view import viewer_callback


def write_pngs_for_report():
    
    stamp = "report"
    show_steps = True
    
    for h in [1.8, 1.6, 1.4, 1.2]:
        interpolate([1,0,0], [0,1,0], h, save_images=stamp+str(h).replace('.','p'), show_steps=show_steps, viewer_callback=viewer_callback)

def do_whole_interpolation(h, divisions):
    if divisions > 10:
        print("Too many divisions, bumping down to 10")
        divisions = 10
        
    print("do_whole_interpolation h=%f" % h)
    interpolate([1,0,0], [0,1,0], h, target_divisions=divisions, show_steps=False, viewer_callback=viewer_callback)
