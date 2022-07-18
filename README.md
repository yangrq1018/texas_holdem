# A Texas Solve

Before you start, it is recommended to create a clean new Conda environment

```
conda create --name "texas_holdem" python==3.10
conda activate texas_holdem
```

> 如果`conda activate`没有效果(如`pip`并非指向新创建的虚拟环境)，可以尝试`conda init`重置shell环境。

Install the necessary dependencies

```
pip install -r requirements.txt
```


## Debug via Visual Studio Code
    - VSCode选择刚刚创建的虚拟环境的解释器
    - 运行VSCode里预先配置好的调试项目`计算给定Hole cards的Histogram`

## Run module via command line
```
python -m holdem -p As 2c
```


```
❯ python -m holdem --help   
Usage: python -m holdem [OPTIONS] [HOLE_CARDS]...

  Calculate the histgram for a hand of 'HOLE_CARDS'. HOLE_CARDS should be
  an array of string representations of ards

Options:
  -p      show progress bar (tqdm based)
  --help  Show this message and exit.
```

牌面的字符串规则

以正则`re.match(r'([AJQKTajqkt]|\d)([dchsDCHS])', card_str)`匹配，第一组为
Rank，第二组为Suit，大小写可以不区分，10以T替代。