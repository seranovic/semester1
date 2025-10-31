# The official repo for all files on the first semester project.

## HPC Access

Connect to vpn.ruc.dk, then ssh into one of the following targets:

- dirac: ```ssh <username>@dirac.ruc.dk```
- bead50: ```ssh -J <username>@dirac.ruc.dk <username>@bead50```
- bead67, with access to jupyter environment:\
  ```ssh -J <username>@dirac.ruc.dk,<username>@bead50 -L 50000:localhost:50000 <username>@bead67```

Alternatively, add this snippet to your ssh config:
```sshconfig
Host dirac
    HostName dirac.ruc.dk
    User <username>

Host bead50
    HostName bead50
    User <username>
    ProxyJump dirac

Host bead67
    HostName bead67
    User <username>
    ProxyJump bead50
    LocalForward 50000 localhost:50000 # Port forwarding for accessing jupyter environment
```
and run ```ssh <dirac-OR-bead50-OR-bead67>```.

## Jupyter

While on bead50, start a jupyter environment on bead67 by running:
```bash
source "/net/debye/jklust/slurm/jupyter as a job/jupyter_slurm_job.sh"
jupyter-gpu -w bead67
```
and following the printed instructions.

## Send/Retrieve Data

You have to clone this repository via dirac, as bead50 and bead67 don't have internet access.

Use rsync from your local machine to copy files to/from the server:
```
rsync <source-path> <destination-path>
```
where a remote path follows the syntax: ```<username>@dirac.ruc.dk:/absolute/path```, or if you've set up your ssh config: ```dirac:/absolute/path```.


## Collecting Data
Once ssh into bead67 has been established run the following commands on separate terminals.

```
nvidia-smi dmon -f <filename> --format csv -o T -i 0 
```

```
python3 powertocsv.py <loops> <filename>
```
Loops sweetspot is around 400
```
python3 benchmark_LJ.py
```


