import argparse

def main():
   parser = argparse.ArgumentParser(prog='CourseDemos', description='OpenGL ISP course demos and homeworks')
   parser.add_argument('startup_demo', nargs='?', default='lecture1',
                    help='Directory of the demo that will show up first (helps to debug)')
   args = parser.parse_args()
   print(args)

if __name__ == "__main__":
   main()