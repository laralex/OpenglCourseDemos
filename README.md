# OpenGL course for ISP 2021 (Skoltech)

## OpenGL resources
* [Official OpenGL API
  reference](https://www.khronos.org/registry/OpenGL-Refpages/gl4/)
* TODO: better API reference
* TODO: OpenGL books
* YouTube:
   * [ThinMatrix](https://www.youtube.com/watch?v=VS8wlS9hF8E&list=PLRIWtICgwaX0u7Rf9zkZhLoLuZVfUksDP),
     an author of OpenGL tutorials, and sole creator of Equilinox game
   * [The
     Cherno](https://www.youtube.com/playlist?list=PLlrATfBNZ98foTJPJ_Ev03o2oq3-GGOS2),
     an author of OpenGL tutorials and creator of Hazel game engine
   * [Jamie King](https://www.youtube.com/user/1kingja) has a few
     well-explaining OpenGL videos

## Computer graphics resources
* TODO: math for computer graphics book
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
    * [javidx9](https://www.youtube.com/c/javidx9/videos), makes a series of
      delibrately old-school graphics approaches, but very well explained
   * [thebennybox](https://www.youtube.com/user/thebennybox), a collection of
     very good explanations of graphics, and graphics optimizations

## Preparations

Option 1. (preferred) Conda environment:

```
conda create --name gl
conda activate gl
conda install -c anaconda pyopengl pyopengl-accelerate
```

Option 2. If you don't mind polluting your default Python environment, then you can
globally install like this:
```
pip install PyOpenGL PyOpenGL_accelerate
```

If anything doesn't work, follow [the link to
PyOpenGl](http://pyopengl.sourceforge.net/), scroll to `Downloading and
Installation` paragraph and follow the instructions

## Usage

The most relevant version of the code is on `main` branch of the repository. The
repository contains:
* Lecture demos
* Homework demos, and those are implemented as "fill in the
  gaps" programs. Complete to see the demo!

You can always start the program using
```
python -m src
```
You should see the window where all the graphics is rendered, along side with UI
controls that let you interact with the demo.

If you're debugging one particular demo, you may start the program with this
demo selected:
```
python -m src --startup_demo hw1
```

If may also want to tweak the default UI parameters in a `ui-defaults.json`
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