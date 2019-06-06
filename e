[1mdiff --git a/rainfall-runoff.ipynb b/rainfall-runoff.ipynb[m
[1mdeleted file mode 100644[m
[1mindex a7fffde..0000000[m
[1m--- a/rainfall-runoff.ipynb[m
[1m+++ /dev/null[m
[36m@@ -1,78 +0,0 @@[m
[31m-{[m
[31m- "cells": [[m
[31m-  {[m
[31m-   "cell_type": "code",[m
[31m-   "execution_count": null,[m
[31m-   "metadata": {},[m
[31m-   "outputs": [],[m
[31m-   "source": [[m
[31m-    "import numpy as np\n",[m
[31m-    "\n",[m
[31m-    "import matplotlib.pyplot as plt\n",[m
[31m-    "from bokeh.io import push_notebook, show, output_notebook; \n",[m
[31m-    "from bokeh.plotting import figure; \n",[m
[31m-    "from bokeh.layouts import column\n",[m
[31m-    "output_notebook()\n",[m
[31m-    "\n",[m
[31m-    "from urllib import request"[m
[31m-   ][m
[31m-  },[m
[31m-  {[m
[31m-   "cell_type": "code",[m
[31m-   "execution_count": null,[m
[31m-   "metadata": {},[m
[31m-   "outputs": [],[m
[31m-   "source": [[m
[31m-    "baseurl=''//waterservices.usgs.gov/nwis/iv/?''\n",[m
[31m-    "format='format=rdb'\n",[m
[31m-    "site='sites=02314495'\n",[m
[31m-    "start=\n",[m
[31m-    "end=\n",[m
[31m-    "url = baseurl+format+'&'+site+'&'+startDT=1951-01-01T00:00%2b0000&endDT=2019-04-19T06:56-0400&parameterCd=00065,00045&siteStatus=all'\n",[m
[31m-    "response = request.urlopen(url)\n",[m
[31m-    "raw = response.read().decode('utf8')"[m
[31m-   ][m
[31m-  },[m
[31m-  {[m
[31m-   "cell_type": "code",[m
[31m-   "execution_count": 1,[m
[31m-   "metadata": {},[m
[31m-   "outputs": [[m
[31m-    {[m
[31m-     "data": {[m
[31m-      "text/plain": [[m
[31m-       "'ab'"[m
[31m-      ][m
[31m-     },[m
[31m-     "execution_count": 1,[m
[31m-     "metadata": {},[m
[31m-     "output_type": "execute_result"[m
[31m-    }[m
[31m-   ],[m
[31m-   "source": [[m
[31m-    "'a'+'b'"[m
[31m-   ][m
[31m-  }[m
[31m- ],[m
[31m- "metadata": {[m
[31m-  "kernelspec": {[m
[31m-   "display_name": "Python 3",[m
[31m-   "language": "python",[m
[31m-   "name": "python3"[m
[31m-  },[m
[31m-  "language_info": {[m
[31m-   "codemirror_mode": {[m
[31m-    "name": "ipython",[m
[31m-    "version": 3[m
[31m-   },[m
[31m-   "file_extension": ".py",[m
[31m-   "mimetype": "text/x-python",[m
[31m-   "name": "python",[m
[31m-   "nbconvert_exporter": "python",[m
[31m-   "pygments_lexer": "ipython3",[m
[31m-   "version": "3.7.1"[m
[31m-  }[m
[31m- },[m
[31m- "nbformat": 4,[m
[31m- "nbformat_minor": 2[m
[31m-}[m
