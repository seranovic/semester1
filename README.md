# The official repo for all files on the first semester project.

## HPC Access

Connect to vpn.ruc.dk, then ssh into one of the following targets:

- dirac - main entry point:\
  ```ssh <username>@dirac.ruc.dk```
- i42 & i43 - internet access for file sync (repo cloning, rsync):\
  ```ssh -J <username>@dirac.ruc.dk <username>@<i42/i43>```
- bead50 - RTX 2080 Ti:\
  ```ssh -J <username>@dirac.ruc.dk <username>@bead50```
- bead67 - RTX 4090:\
  ```ssh -J <username>@dirac.ruc.dk <username>@bead67```

Alternatively, add this snippet to your ssh config:

```sshconfig
Host dirac
    HostName dirac.ruc.dk
    User <username>

Host i42 i43 bead50 bead67
    User <username>
    ProxyJump dirac
```

and run ```ssh <target-hostname>```.

## Collecting Data

Set up preferred system sizes in ```main.py```.

While on bead67, run ```main.py``` to start the benchmark and save the measurements to csv:

```sh
# Example: run gamdpy with autotuning and save data with the prefix "default"
python3 main.py -p default gamdpy -a
```

You can use the following arguments:

```
usage: main.py [-h] [-p [PREFIX]] [-d] {gamdpy,lammps} ...

positional arguments:
  {gamdpy,lammps}       backend

options:
  -h, --help            show this help message and exit
  -p, --prefix [PREFIX]
                        identifying prefix for this run (can overwrite data if not unique)
  -d, --debug           run benchmark with small system sizes (~30-60 seconds per run)

# for gamdpy
usage: main.py gamdpy [-h] [-a]

options:
  -h, --help      show this help message and exit
  -a, --autotune  enable autotuning

# for lammps
usage: main.py lammps [-h]

options:
  -h, --help  show this help message and exit
```

Data is written to disk after each measurement, so you can check the progress with ```tail -f data/<filename>.csv```.

## Send/Retrieve Data

Use rsync from your local machine to copy files to/from the server:

```
rsync <source-path> <destination-path>
```

where a remote path follows the syntax: ```<username>@dirac.ruc.dk:/absolute/path```, or if you've set up your ssh config: ```dirac:/absolute/path```.
