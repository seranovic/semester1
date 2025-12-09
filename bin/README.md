# Build instructions

```sh
git clone https://github.com/lammps/lammps -d develop
cd lammps
git reset --hard 84e757fcc66c6f2de7fdb6ec86c637c41df86789

mkdir build && cd build
cmake ../cmake \
    -D PKG_GPU=yes \
    -D GPU_API=cuda \
    -D GPU_ARCH=sm89

cmake --build .
```
