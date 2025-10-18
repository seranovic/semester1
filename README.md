# The official repo for all files on the first semester project.

## Access bead50

1. Connect to the vpn
2. SSH into bead50:
    - Run ```ssh -J <username>@dirac.ruc.dk <username>@bead50```

      **OR**
    - Add this snippet to your ssh config:
        ```sshconfig
        Host dirac
            HostName dirac.ruc.dk
            User <username>
        
        Host bead50
            HostName bead50
            User <username>
            ProxyJump dirac
        ```
        and run ```ssh bead50```

## Access bead67

While on bead50, start a jupyter environment on bead67 by running:
```bash
source "/net/debye/jklust/slurm/jupyter as a job/jupyter_slurm_job.sh"
jupyter-gpu -w bead67
```
