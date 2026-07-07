# Project Title: The AMIHANEN-Analysis-Engine-v.12

```
PROGRAM AUTHOR
--------------

Lian Rich A. Romano
    - Position: Scretary and Assisting Lead
    - Role: Software Engineering, Statistics
```

Imagine a world where power didn't exist. Physically, it would be dark. But what about its impact on people? If anything, it's worse than dark; it becomes hopeless. Northern Mindanao struggles to secure power regionwide, affecting all consumers, from households to economic centers. Furthermore, electrical hazards are common in the Philippines since communities actively rely on poorly managed electrical cables. Furthermore, solar systems have more recently been associated with rising death tolls among avian species.

With this in mind, AMIHANEN (Acoustic Mechanical Impulse Harvester Attached to a Noise-to-Energy Nanogenerator) was engineered to promote autonomous wireless power. To evaluate AMIHANEN's performance, the AMIHANEN Analysis Engine was used in processing the results for the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System.

```
Program Bash Commands

For main analyses            -->   :   python main.py amihanen_dataset.csv
For glm testing/selection    -->   :   python glm_selector.py amihanen_dataset.csv
```

This engine was engineered using Gemini 3.1 Pro and ChatGPT 5.5 (Thinking), both using free tier plans. However, the final code for each version became more and more complex after each revision and addition, bloating the code with multiple versions per document as you can see in the prompt documents @ the [prompt-docs](.//prompt-docs/) folder. To avoid this, the researchers re-configured the analysis engine with less files than the previous 11 versions as recorded by each document in the [prompt-docs](.//prompt-docs/) folder, reducing bulk and weight.

```
COPYRIGHT NOTICE:

This engine is the sole work of Lian Rich A. Romano while the results and product of the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System belong equally to all the authors.

No part of any of these works may be reproduced without the formal consent of all the authors involved, whether for the AMIHANEN Analysis Engine or for the study AMIHANEN: The Feasibility of Integrating Wireless Electrotransmission in an Acoustic Energy Harvesting System.

(C) 2026. Lian Rich A. Romano. All Rights Reserved. 
```
