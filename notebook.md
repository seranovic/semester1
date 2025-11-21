# Interactive examples of data presentation


```python
import pandas as pd
import seaborn.objects as so
```

## Data structure


```python
# FIXME: set identifier prefix and simulator
identifier = "default"
sim = "gamdpy"  # one of gamdpy, gamdpy-at, lammps

df = pd.read_csv(f"data/{identifier}-{sim}.csv")
```

## Presentation & analysis

### Stacked graphs

Displays two graphs stacked on top of each other. Easily readable.


```python
p = (
    so.Plot(data=df, x=df.time)
    .add(so.Area(edgewidth=0), y="total")
    .add(so.Line(linewidth=1), y="total", label="Total")
    .add(so.Area(edgewidth=0, color="green"), y="gpu")
    .add(so.Line(linewidth=1, color="green"), y="gpu", label="GPU")
    .label(
        x="Time (s)",
        y="Power draw (W)",
        title=f"{sim} {identifier}",
        legend="Hardware measured"
    )
)
#p.save(f"fig/{identifier}-{sim}-stacked")  # uncomment to save
p
```




    
![png](notebook_files/notebook_6_0.png)
    



### Paired graph

Displays two graphs side by side. Might have a purpose in the report later on.


```python
p = (
    so.Plot(data=df, x=df.time)
    .pair(y=["gpu", "total"])
    .add(so.Area(edgewidth=0)).add(so.Line(linewidth=1))
    .label(
        x="Time (s)",
        y0="GPU power draw (W)",
        y1="Total power draw (W)",
        title=f"{sim} {identifier}"
    )
)
#p.save(f"fig/{identifier}-{sim}-paired")
p
```




    
![png](notebook_files/notebook_8_0.png)
    



### Band graph

Displays the interval between two y-values. Looks kinda goofy at this point.


```python
p = (
    so.Plot(df, x=df.time, ymin="gpu", ymax="total")
    .add(so.Band(edgewidth=1))
    .label(
        x="Time (sec)",
        y="Power draw (W)",
        title=f"Power draw - {sim} {identifier}"
    )
)
#p.save(f"fig/{identifier}-{sim}-band")
p
```




    
![png](notebook_files/notebook_10_0.png)
    


