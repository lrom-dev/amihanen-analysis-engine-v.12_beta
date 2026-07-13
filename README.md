The Official AMIHANEN Analysis Engine
-----------------

Project Author: Lian Rich A. Romano

This engine analyzes the results for the study "AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System". On June 14, 2026, the researchers of the study found that the statistical software they were currently using lacked multiple features. To bridge this gap, the researchers decided to develop their own analysis engine specifically tailored to this study.


The Project
-----------------

```
ECs struggle to secure power for Nothern Mindanao, leading to frequent outages, while the rest of the Philippines actively relies on substandard infrastructure to power communities, leading to growing reports of electrical injuries. Furthermore, solar systems have recently been associated with the "lake effect", a phenomenon leading a global death toll among avian species. In support of UN SDGs 9 (Industry, Innovation, and Infrastructure), 11 (Sustainable Cities and Communities), and 15 (Life on Land), AMIHANEN (Acoustic Mechanical Impulse Harvester Attached to a Noise-to-Energy Nanogenerator) is engineered as a pilot project in addressing all three issues together by providing an autonomous energy solution without relying on any major external infrastructure or any material associated with light polarization.
```

The researchers began developing the engine on June 14, 2026, and has since undergone 12 versions. It was engineered using ChatGPT 5.5 (Free tier) and Gemini 3.1 Pro (Free tier), where the 11 previousy versions of the engine came from each conversation (1 version per session). This can be found in the [prompt-docs](.//prompt-docs/).


```
Program Bash Commands

For main analyses            -->   :   python main.py
For glm testing/selection    -->   :   python glm_selector.py amihanen_dataset.csv
```

This engine was engineered using Gemini 3.1 Pro and ChatGPT 5.5 (Thinking), both using free tier plans. However, the final code for each version became more and more complex after each revision, bloating the code with multiple versions per document as you can see in the prompt documents @ the [prompt-docs](.//prompt-docs/) folder. To avoid this, the researchers re-configured the analysis engine with less files than the previous 11 versions as recorded by each document in the [prompt-docs](.//prompt-docs/) folder, reducing bulk and weight.

```
COPYRIGHT NOTICE:

This engine is the sole work of Lian Rich A. Romano while the results and product of the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System belong equally to all the authors.

No part of any of these works may be reproduced without the formal consent of all the authors involved, whether for the AMIHANEN Analysis Engine or for the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System.

(C) 2026. Lian Rich A. Romano. All Rights Reserved. 
```
Note: All dependencies are listed in [requirements.txt](.//requirements.txt). The raw data is encoded in [amihanen_dataset.csv](.//amihanen_dataset.csv).
