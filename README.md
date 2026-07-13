# **The AMIHANEN Analysis Engine**

***Project Author: Lian Rich A. Romano***

This engine analyzes the results for the study "AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System". On June 14, 2026, the researchers of the study found that the statistical software they were currently using lacked multiple features. To bridge this gap, the researchers decided to develop their own analysis engine specifically tailored to this study.


**1. The Project**
---

***ABSTRACT:***
```
ECs struggle to secure power for Nothern Mindanao, leading to frequent outages, while the rest of the Philippines actively relies on substandard infrastructure to power communities, leading to growing reports of electrical injuries. Furthermore, solar systems have recently been associated with the "lake effect", a phenomenon leading a global death toll among avian species. In support of UN SDGs 9 (Industry, Innovation, and Infrastructure), 11 (Sustainable Cities and Communities), and 15 (Life on Land), AMIHANEN (Acoustic Mechanical Impulse Harvester Attached to a Noise-to-Energy Nanogenerator) is engineered as a pilot project in addressing all three issues together by providing an autonomous energy solution without relying on any major external infrastructure or any material associated with light polarization.
```

The researchers began developing the engine on June 14, 2026, and has since undergone 12 versions. It was engineered using ChatGPT 5.5 (Free tier) and Gemini 3.1 Pro (Free tier), where each conversation created its own discrete version (1 version per session). This can be found in the [prompt-docs](.//prompt-docs/).


***PROGRAM BASH:***
```
For main analyses            -->   :   python main.py
For glm testing/selection    -->   :   python glm_selector.py amihanen_dataset.csv
```

This engine was engineered using Gemini 3.1 Pro and ChatGPT 5.5 (Thinking), both using free tier plans. However, the final code for each version became more and more complex after each revision, bloating the code with multiple versions per document as you can see in the prompt documents @ the [prompt-docs](.//prompt-docs/) folder. To avoid this, the researchers re-configured the analysis engine with less files than the previous 11 versions as recorded by each document in the [prompt-docs](.//prompt-docs/) folder, reducing bulk and weight.

***COPYRIGHT NOTICE:***
```
This engine is the sole work of Lian Rich A. Romano while the results and product of the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System belong equally to all the authors.

No part of any of these works may be reproduced without the formal consent of all the authors involved, whether for the AMIHANEN Analysis Engine or for the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System.

(C) 2026. Lian Rich A. Romano. All Rights Reserved. 
```
Note: All dependencies are listed in [requirements.txt](.//requirements.txt). The raw data is encoded in [amihanen_dataset.csv](.//amihanen_dataset.csv).

**2. Statistical Methods**
---
In March 2026, the university statistician of La Salle University - Ozamiz trained the researchers in using jamovi during a workshop-seminar. With this in mind, AMIHANEN's research team approached the university statistician for advice on the study's statistical treatment. During this discussion, the university statistician recommended looking into the non-parametric properties of our raw data and suggested the Mann-Whitney U (Wilcoxon Rank-Sum) and Kruskal-Wallis H tests to infer the differences between both of our harvesters under controlled conditions (2 x 3 x 5 full factorial). Then, the researchers decided on the following statistics, per question, to report for the final article:

***Objectives***
1.  What is the minimum sound pressure threshold (dBth) required for both harvesters to begin generating power, and how does Sound Pressure Level (SPL) correlate with DC power generation (Pdc)?
```
    - Boolean Threshold Analysis
    - Variability (Minimum)
    - Spearman's Correlation Coefficient (ρ)
```
2.  What are the median, minimum, and maximum Vdc, Idc, and Pdc of the standalone and integrated harvesters after one minute at each SPL under simulated laboratory conditions? Furthermore, how dispersed are the results according to median absolute deviation (MAD)?
```
    - Central Tendency (Median/Mdn)
    - Variability (Min., Max., Median Absolute Deviation [MAD])
```
3.  Is there any significant difference between the Vdc, Idc, and Pdc of the standalone and integrated harvesters? Furthermore, how do architecture type, SPL, and environment affect Vdc, Idc, and Pdc and how do all these factors interact in affecting power generation?
```
    - Mann-Whitney U (Wilcoxon Rank-Sum)
    - Kruskal-Wallis H
    - Generalized Linear Model (Tweedie-Log, power = 1.5)
```

***A short note on the Spearman's, the t-value was manually calculated from the equation ρ * (n-2/1-p^2)^0.5***

**3. Metadata**
---

***The Harvesters and the Hypothesis***

This study deals with experimenting two harvesters to determine the feasibility of integrating Wireless Electrotransmission and Acoustic Energy Harvesting. As such, there are two harvesters: standalone (without WPT) and integrated (with WPT).

Tested at ɑ = .05, the null hypothesis reads: *There is no significant difference between the performance of the standalone and integrated harvesters in terms of generated output (Vdc, Idc, and Pdc).*

***2 x 3 x 5 Full Factorial***

The study is designed in a 2 x 3 x 5 full factorial, where 2 represents the two harvesters (standalone, integrated), 3 represents the chosen environments (highway, restaurant, boat engine), and 5 represents the five SPLS (60, 70, 80, 90, 100 dB). Conditions were isolated in a controlled environment.

***Homogeneity, Dispersion, Variability***
<table>
  <thead>
    <tr>
      <th rowspan="2">Variable</th>
      <th rowspan="2">Setup</th>
      <th colspan="2">Skewness</th>
      <th colspan="2">Kurtosis</th>
      <th colspan="2">Shapiro-Wilk</th>
    </tr>
    <tr>
      <th>Skew</th>
      <th>SE</th>
      <th>Kurtosis</th>
      <th>SE</th>
      <th>W</th>
      <th>p</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2" align="center"><b>1</b></td>
      <td align="center">A</td>
      <td align="center">3.41</td>
      <td align="center">0.35</td>
      <td align="center">10.52</td>
      <td align="center">0.69</td>
      <td align="center">0.38</td>
      <td align="center">&lt;.001</td>
    </tr>
    <tr>
      <td align="center">B</td>
      <td align="center">NaN</td>
      <td align="center">0.35</td>
      <td align="center">NaN</td>
      <td align="center">0.69</td>
      <td align="center">NaN</td>
      <td align="center">NaN</td>
    </tr>
    <tr>
      <td rowspan="2" align="center"><b>2</b></td>
      <td align="center">A</td>
      <td align="center">3.41</td>
      <td align="center">0.35</td>
      <td align="center">10.52</td>
      <td align="center">0.69</td>
      <td align="center">0.38</td>
      <td align="center">&lt;.001</td>
    </tr>
    <tr>
      <td align="center">B</td>
      <td align="center">NaN</td>
      <td align="center">0.35</td>
      <td align="center">NaN</td>
      <td align="center">0.69</td>
      <td align="center">NaN</td>
      <td align="center">NaN</td>
    </tr>
    <tr>
      <td rowspan="2" align="center"><b>3</b></td>
      <td align="center">A</td>
      <td align="center">3.61</td>
      <td align="center">0.35</td>
      <td align="center">10.52</td>
      <td align="center">0.69</td>
      <td align="center">0.29</td>
      <td align="center">&lt;.001</td>
    </tr>
    <tr>
      <td align="center">B</td>
      <td align="center">NaN</td>
      <td align="center">0.35</td>
      <td align="center">NaN</td>
      <td align="center">0.69</td>
      <td align="center">NaN</td>
      <td align="center">NaN</td>
    </tr>
  </tbody>
</table>

<p><i>Note.</i> H<sub>a</sub>: non-normal, H<sub>0</sub>: normal</p>


Testing The Engine
---
