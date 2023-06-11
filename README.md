# OpenGL course for ISP (Skoltech)

## OpenGL resources
> I can't really suggest OpenGL books. Just beware that books older than 2010 may describe OpenGL 2, which is very obsolete and inefficient.
* OpenGL documentation
  * [Official OpenGL API
    reference](https://www.khronos.org/registry/OpenGL-Refpages/gl4/)
  * [Arguably better web-site with OpenGL API reference](https://docs.gl/)
* Step-by-step guides
  * [Learnopengl.com](https://learnopengl.com/)
  * [OpenGL-tutorial.org](http://www.opengl-tutorial.org/)
  * [Open.gl](https://open.gl/)

* YouTube:
  * [ThinMatrix](https://www.youtube.com/watch?v=VS8wlS9hF8E&list=PLRIWtICgwaX0u7Rf9zkZhLoLuZVfUksDP),
     an author of OpenGL tutorials, and the sole creator of Equilinox game
  * [The
     Cherno](https://www.youtube.com/playlist?list=PLlrATfBNZ98foTJPJ_Ev03o2oq3-GGOS2),
     an author of OpenGL tutorials and the creator of Hazel game engine
  * [Victor Gordan](https://www.youtube.com/c/VictorGordan/videos), follows Learnopengl.com guide in a video format
  * [Brian Will](https://www.youtube.com/user/briantwill/featured), awesome
      explanations of OpenGL and computer graphics concepts
  * [Jamie King](https://www.youtube.com/user/1kingja) has a few
     well-explaining OpenGL and computer graphics videos

## Computer graphics resources
* [Scratchapixel.com](https://www.scratchapixel.com/index.php?redirect) -
  quite a few good articles on computer graphics, ray tracing
* [Real-time rendering courses hosted by SIGRAPH conference](https://advances.realtimerendering.com/)
  presentations from computer graphics leaders, posted every year since 2006 to 2021
* [Foundations of Game Engine
  Development](https://foundationsofgameenginedev.com/) by Eric Lengyel - a
  legendary 4-books series about computer graphics math, rendering, materials,
  physics
* [Mathematics for 3D Game Programming and Computer Graphics, Third
  Edition](https://www.amazon.com/Mathematics-Programming-Computer-Graphics-Third/dp/1435458869)
  a bit older book by Eric Lengyel
* [Computer Graphics from Scratch: A Programmer's Introduction to 3D
  Rendering](https://www.amazon.com/Computer-Graphics-Scratch-Gabriel-Gambetta/dp/1718500769)
 by Gabriel Gambetta  - I haven't read it yet, but seems easy and fun
* YouTube
   * [Sebastian Lague](https://www.youtube.com/c/SebastianLague), definitely
     check it out, every video is
     a joy to watch
   * [Casey Muratori](https://www.youtube.com/c/MollyRocket), a very
    talented programmer and an author of over 1000 hours of live game coding
    videos (doubt anyone could watch it completely)
    * [The Art of
      Code](https://www.youtube.com/channel/UCcAlTqd9zID6aNX3TzwxJXg), teaches
      how to create very cool looking fragment shaders (not OpenGL, but rather
      [Shadertoy](https://www.shadertoy.com/) which is 99% similar to OpenGL
      fragment shaders)
    * [Martin Donald](https://www.youtube.com/c/MartinDonald), has only a few short ideos, but extremely interesting and well explained
    * [javidx9](https://www.youtube.com/c/javidx9/videos), makes a series of
      deliberately old-school graphics approaches, but very well explained
   * [thebennybox](https://www.youtube.com/user/thebennybox), a collection of
     very good explanations of graphics, and graphics optimizations

## Installation

We will be using a few Python libraries. Why? OpenGL **only** can manage
GPU drawing (configuring GPU, sending/receiving data to GPU), it **can't** 
make windows and user interfaces in your operating system, it **doesn't**
include mathematical primitives common in computer graphics,
 it's **doesn't** have anything for data parsing (e.g. 3D
model files) and decoding (e.g. uncompressing JPEG or PNG images).

Thus, we'll use:
* PyOpenGL (plus PyOpenGl_accelerate) - provides access to OpenGL API from Python
* PyGLFW - manages cross-platform creation of windows (also available in C/C++ programming languages)
  and interation using keyboard/mouse
* Pyrr - math functions commonly used in computer graphics
* Imgui - fancy user-interface elements
* Pillow - encoding and decoding image files
* PyWavefront - decoding 3D models files in OBJ format

Option 1. (preferred) Anaconda environment:

```
conda create --name gl
conda activate gl
conda install -c conda-forge pyopengl-accelerate pyglfw pyrr pillow
pip install imgui[glfw] pywavefront
```

Option 2. If you don't mind polluting your default Python environment, then you can
globally install like this:
```
pip install PyOpenGL PyOpenGL_accelerate glfw pyrr pillow imgui[glfw] pywavefront
```

## !!!

You may have troubles when installing those packages.
* To fix PyOpenGL, try to follow [its official page
PyOpenGL](http://pyopengl.sourceforge.net/), scroll to `Downloading and
Installation` paragraph and follow the instructions
* To fix GLFW, try to follow [its official
  repository](https://github.com/FlorianRhiem/pyGLFW#installation) and install
  additional library for your OS

## How to use this repository

The most relevant version of the code is on the `main` branch of the repository. The
repository contains:
* Lecture demos
* Homework demos, and those are implemented as "fill in the
  gaps" programs. Complete to see the demo!

This command should open a window with a running visualization, and UI controls that allow your interaction.
```
python run.py
```

If you're debugging one particular demo, it may be convenient to start the application with this demo right away.
```
python run.py hw1
```

If may also want to tweak the default UI parameters in a `ui_defaults.json`
config of the particular demo folder.

## How to work on homeworks

It might be challenging for some people to write their code and then try to
get the latest updates from this repository. In order to preserve your own
sanity, I suggest the following workflow:

1. **If you need to change files, create a separate `git` branch first**
```
git branch my_branch
```

2. Before writing your code, make sure you're on your branch (and not `main`
   branch).
```
git checkout my_branch
```

3. Make your changes in the files, commit them whenever you like
```
git add myfile_1.py myfile_2.py
# or if you're confident:
git add --all 

# then
git commit -m "Message of my commit"
```

4. Now suppose that you want to download the latest changes from this
   repository. Even while you're on you own branch `my_branch`, you should still
   be able to execute this, to get the latest updates
```
git fetch origin main:main
```
This will update content of the `main` branch, so your code is preserved. In order
to combine updates and your own code, you better commit your changes as shown in
item #3 of this list.

Next, execute this, **while still being on `my_branch`**
```
git merge main
```

This will attempt merging the code. If you're lucky and your code doesn't
conflict with the updates, then the process will finish successfully.
Otherwise you may see the message
> CONFLICT (content): Merge conflict in
>
> Automatic merge failed; fix conflicts and then commit the result.

This means, that you'll have to manually resolve the conflicts. This topic is
quite complicated, so either:

* Try [manual](https://docs.github.com/en/github/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line) conflict resolutions
* Install a [graphical tool for merging](https://www.slant.co/topics/48/~best-visual-merge-tools-for-git), and use `git mergetool`
* Contact me for help!

After fixing the conflicts, there's a chance you've broken something. Try to
launch the program to verify that no errors/exceptions are shown. If everything
is OK, you need to continue merging
```
git merge --continue
```
You may be prompted to enter a commit message to finally finish the merge. And
after that the updates should be added. Run the program again to double
check that everything works.
