
import glob

def go():
    paths = glob.glob("diagrams/*.png")
    for path in paths:
        print('<img src="%s"><br><br>' % path)

if __name__=="__main__":
    go()
