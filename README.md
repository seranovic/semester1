# The official repo for all files on the first semester project.

## HPC Access

Connect to vpn.ruc.dk, then ssh into one of the following targets:

- dirac: ```ssh <username>@dirac.ruc.dk```
- bead50: ```ssh -J <username>@dirac.ruc.dk <username>@bead50```
- bead67: ```ssh -J <username>@dirac.ruc.dk,<username>@bead50 -L 50000:localhost:50000 <username>@bead67```

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

## Collecting Data
Once ssh into bead67 has been established run the following commands on separate terminals.

```
nvidia-smi dmon -f <filename> --format csv -o T -id 0 
```

```
python3 powertocsv.py <loops> <filename>
```
Loops sweetspot is around 330.
```
python3 benchmark_LJ.py
```


