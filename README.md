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

While on bead67, run the following script to start the benchmark and save the measurements to csv:
```sh
python3 main.py
```
Data will by default be saved with the identifier-prefix "default".

You can use the following arguments:

```
usage: main.py [-h] [identifier]

positional arguments:
  identifier  identifier for this run (will overwrite data if not unique)

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

## Jupyter

While on bead50, start a jupyter environment on bead67 by running:
```bash
source "/net/debye/jklust/slurm/jupyter as a job/jupyter_slurm_job.sh"
jupyter-gpu -w bead67
```
and following the printed instructions.
