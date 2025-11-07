# The official repo for all files on the first semester project.

## HPC Access

Connect to vpn.ruc.dk, then ssh into one of the following targets:

- dirac - main entry point:\
  ```ssh <username>@dirac.ruc.dk```
- i42 & i43 - internet access for file sync:\
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

## Jupyter

While on bead50, start a jupyter environment on bead67 by running:
```bash
source "/net/debye/jklust/slurm/jupyter as a job/jupyter_slurm_job.sh"
jupyter-gpu -w bead67
```
and following the printed instructions.

## Send/Retrieve Data

You have to clone this repository and transfer data via i42/i43.

Use rsync from your local machine to copy files to/from the server:
```
rsync <source-path> <destination-path>
```
where a remote path follows the syntax: ```<username>@dirac.ruc.dk:/absolute/path```, or if you've set up your ssh config: ```dirac:/absolute/path```.


## Collecting Data

While on bead67, run the following script to start the benchmark and save the measurements to csv:
```sh
python3 main.py
```
The default parameters will run for 435 seconds and save the csv-files with the prefix "default".

You can use the following arguments:
```
usage: main.py [-h] [-i [name]] [-s [n]]

options:
  -h, --help         show this help message and exit
  -i, --id [name]    unique identifier for this run
  -s, --samples [n]  amount of samples to run (1 sample/sec)
```
