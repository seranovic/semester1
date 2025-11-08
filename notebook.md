# Interactive examples of data presentation


```python
import pandas as pd
import seaborn.objects as so
```

## Data structure


```python
identifier = "default"  # FIXME: set identifier of csv dataset

gpu = pd.read_csv(f"csv/{identifier}-gpu.csv")
gpu = pd.DataFrame({
    "time": gpu["time"],
    "power": gpu["power"],
})

total = pd.read_csv(f"csv/{identifier}-total.csv")

combined = pd.merge(gpu, total, how="inner", on="time", suffixes=("_gpu", "_total"))
combined
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>power_gpu</th>
      <th>power_total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>23:16:44</td>
      <td>14</td>
      <td>133.11</td>
    </tr>
    <tr>
      <th>1</th>
      <td>23:16:45</td>
      <td>14</td>
      <td>125.67</td>
    </tr>
    <tr>
      <th>2</th>
      <td>23:16:46</td>
      <td>14</td>
      <td>125.67</td>
    </tr>
    <tr>
      <th>3</th>
      <td>23:16:47</td>
      <td>14</td>
      <td>128.87</td>
    </tr>
    <tr>
      <th>4</th>
      <td>23:16:48</td>
      <td>14</td>
      <td>130.47</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>427</th>
      <td>23:23:54</td>
      <td>17</td>
      <td>151.94</td>
    </tr>
    <tr>
      <th>428</th>
      <td>23:23:55</td>
      <td>17</td>
      <td>156.72</td>
    </tr>
    <tr>
      <th>429</th>
      <td>23:23:56</td>
      <td>17</td>
      <td>142.70</td>
    </tr>
    <tr>
      <th>430</th>
      <td>23:23:57</td>
      <td>17</td>
      <td>143.10</td>
    </tr>
    <tr>
      <th>431</th>
      <td>23:23:58</td>
      <td>17</td>
      <td>156.27</td>
    </tr>
  </tbody>
</table>
<p>432 rows × 3 columns</p>
</div>



## Presentation & analysis

### Stacked graphs

Displays two graphs stacked on top of each other. Easily readable.


```python
(
    so.Plot(data=combined, x=combined.index)
    .add(so.Area(edgewidth=0), y="power_total")
    .add(so.Line(linewidth=1), y="power_total", label="Total")
    .add(so.Area(edgewidth=0, color="green"), y="power_gpu")
    .add(so.Line(linewidth=1, color="green"), y="power_gpu", label="GPU")
    .label(
        x="Time (s)",
        y="Power draw (W)",
        title=f"gamdpy {identifier}",
        legend="Hardware measured"
    )
)#.save(f"fig/{identifier}-stacked")  # uncomment to save
```




    
![png](notebook_files/notebook_6_0.png)
    



### Paired graph

Displays two graphs side by side. Might have a purpose in the report later on.


```python
(
    so.Plot(data=combined, x=combined.index)
    .pair(y=["power_gpu", "power_total"])
    .add(so.Area(edgewidth=0)).add(so.Line(linewidth=1))
    .label(
        x="Time (s)",
        y0="GPU power draw (W)",
        y1="Total power draw (W)",
        title=f"gamdpy {identifier}"
    )
)#.save(f"fig/{identifier}-paired")
```




    
![png](notebook_files/notebook_8_0.png)
    



### Band graph

Displays the interval between two y-values. Looks kinda goofy at this point.


```python
(
    so.Plot(combined, x=combined.index, ymin="power_gpu", ymax="power_total")
    .add(so.Band(edgewidth=1))
    .label(
        x="Time (sec)",
        y="Power draw (W)",
        title=f"Power draw - gamdpy {identifier}"
    )
)#.save(f"fig/{identifier}-band")
```




    
![png](notebook_files/notebook_10_0.png)
    


