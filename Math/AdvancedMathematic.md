<head>
    <script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
            skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
            inlineMath: [['$','$']]
            }
        });
    </script>
</head>

## [主页](../README.md)/[Math](./readme.md)/高等数学

### 第一章 映射与函数
#### 第一节
  $f[g(x)]$  函数中g与f能构成复合函数的条件为:函数g的值  $R_{g}$  必须包含于函数f的定义域  $D_{f}$  ,即  $R_{g}$    $\subset$  $D_{f}$    

- 函数的运算
  - 和(差)f  $\pm$  g：(f  $\pm$  g)(x)=  $f(x)$    $\pm$  $g(x)$  ,x  $\in$  D;
  - 积f  $\cdot$  g:(f  $\cdot$  g)(x)=  $f(x)$    $\cdot$    $g(x)$  ,x  $\in$  D;
  - 商f  $\div$  g:(  $\frac{f}{g}$  )(x)=  $\frac{f(x)}{g(x)}$  ,x  $\in$  D\{x|g(x)=0,x  $\in$D  }
  
- 初等函数
  - **幂函数**：y  =$x^{b}$  (b  $\in  $R是常数)
  - **指数函数**：y=  $a^{x}$  (a>o且a   $\neq$  1)
  - **对数函数**：y=  $\log_ax$  (a>0且a  $\neq$  1,当a=e时，为y=  $\ln(x)$  ) 
  - **三角函数**：y=  $\sin x$  , y=  $\cos x$  , y=  $\tan x$  
  - **反三角函数**：y=  $\arcsin x$  , y=  $\arccos x$  , y=  $\arctan x$   等等
  - 有常数和基本初等函数经过有限次的四则运算和有限次的函数复合步骤所构成并可用一个式子表示的函数，称为初等函数
  - **双曲正弦**：  $\sh x$  =  $\frac{e^{x}-e^{-x}}{2}$  ,定义域(-  $\infty$  ,+  $\infty$  ),为奇函数，通过原点且关于原点对称，在定义域内其单调递增。
  - **双曲余弦**：  $\ch x$  =  $\frac{e^{x}+e^{-x}}{2}$  ,定义域(-  $\infty$  ,+  $\infty$  )，为偶函数，通过点(0,1)且关于y轴对称，在(-  $\infty$  ,0)其单调递减，在(0,+  $\infty$  )其单调递增
  - **双曲正切**：  $\th x$  =  $\frac{\sh x}{\ch x}$  =  $\frac{e^{x}-e^{-x}}{e^{x}+e^{-x}}$  ,定义域(-  $\infty$  ,+  $\infty$  )，为奇函数，通过原点且关于原点对称，在定义域内其单调递增。
  - ![](/Math/pic/Math1.png)
  - 由双曲函数定义可得：
    -   $sh (x+y)$  =  $sh xch y$  +  $ch xsh y$  
    -   $sh (x-y)$  =  $sh xch y$  -  $ch xsh y$  
    -   $ch (x+y)$  =  $ch xch y$  +  $sh xch y$  
    -   $ch (x-y)$  =  $ch xch y$  -  $sh xsh y$  
#### 第二节 数列极限
- 定义 设{  ${x}_{n}$  }为一数列，如果存在常数a，对于任何给定的正数  $\alpha$  (无论它多么小)，总存在正整数N，使得当n>N时，不等式  $\lvert {x}_{n}-a\rvert$  <  $\alpha$  都成立，那么**称常数a是数列{  ${x}_{n}$  }的极限**，或者称数列{  ${x}_{n}$  }收敛于a，记为  $\underset{x\rightarrow\infty}{\lim}$  =a,或  ${x}_{n}$  ->a( n->  $\infty$  )
- 收敛数列的性质：
  - 定理一：如果数列{  ${x}_{n}$  }收敛，那么它有唯一的极限
![](/Math/pic/Math2.png)
  - 对于数列{  ${x}_{n}$  }，如果存在正数M，使得对于一切  ${x}_{n}$  都满足不等式{  ${x}_{n}$  }  $\le$  M,称数列{  ${x}_{n}$  }是有界的，如不满足则称为无界的。
  - 定理二：如果数列{  ${x}_{n}$  }是收敛的，那么它是一定有界。
  - 定理三：如果  $\underset{x\rightarrow\infty}{\lim}$    ${x}_{n}$  =a，且a>0(或a<0)，那么存在正整数N，当n>N时，都有  ${x}_{n}$  >0(  ${x}_{n}$  <0)
    - 推论：如果数列{  ${x}_{n}$  }从某项起有  ${x}_{n}$    $\le$  0(或  $\ge$  0),那么a  $\le$  0(或  $\ge$  0)
  - 定理四：如果数列{  ${x}_{n}$  }收敛于a，那么它的任一子数列也收敛，且极限也是a.
#### 第三节 函数的极限
- 函数  $f(x)$  的极限概念中，x是既从  ${x}_{0}$  左侧也从  ${x}_{0}$  右侧趋于  ${x}_{0}$  的。
- 在  $\underset{x\rightarrow\infty}{\lim}$    $f(x)$  =  $A$  的定义中，把0<  $\lvert {x}-{x}_{0}\rvert$  <  $\delta  $,改为  ${x}_{0}$  -  $\delta$  <  $x$  <  ${x}_{0}$  ,那么  $A$  就称为函数  $f(x)$  的左极限，右极限反之。  $f({x}_{0}^{-})$  =  $A$  
  - 左，右极限被称为单侧极限。 
![](/Math/pic/Math3.png)
![](/Math/pic/Math4.png)
- 函数极限的性质：
  - 定理一：(函数极限的唯一性)如果  $\underset{x\rightarrow{x}_{0}}{\lim}$    $f(x)$   存在，那么这极限唯一。
  - 定理二：(函数极限的局部有界性)如果  $\underset{x\rightarrow{x}_{0}}{\lim}$    $f(x)$  =   $A$  ，那么存在常数M>0和   $\delta$  >0,使得当0<  $\lvert {x}-{x}_{0}\rvert$   <   $\delta$  时，有  $\lvert f(x)\rvert$    $\le$  M.
  - 定理三：(函数极限的局部保号性)如果  $\underset{x\rightarrow{x}_{0}}{\lim}$    $f(x)$  =A，且A>0(或A<0),那么存在常数  $\delta$  >0，使得当0<  $\lvert {x}-{x}_{0}\rvert$  <  $\delta$  时，有f(x)>0(或f(x)<0)
#### 第四节 无穷小与无穷大
##### 无穷小
- 定义一：如果函数f(x)当  $x$    $\rightarrow$    ${x}_{0}$  时的极限为0，那么称函数当前状况为无穷小
- 定理一：在自变量的同一变化过程x  $\rightarrow$    ${x}_{0}$  (或x趋近于无限大)，函数  $f(x)$  具有极限值A的充分不必要条件是  $f(x)$  =A+a,其中a是无穷小。
##### 无穷大
- 当  $f(x)$  为无穷小时,  $\frac{1}{f(x)}$  为无穷大。当  $f(x)$  为无穷大时，则反之。
#### 第五节 极限运算法则
- 定理一：两个无穷小之和为无穷小，有限个无穷小之和仍为无穷小。    
- 定理二：有界(总是小于或大于某一个值)与无穷小的积为无穷小。例：  $\underset{x\rightarrow{0}}{\lim}$    $sin(\frac{1}{x})*x$  =0,三角函数永远是有界的。
- 推论一：c(常数)*无穷小是无穷小。
- 推论二：有限个无穷小的积是无穷小。
- 定理三：  $\underset{}{\lim}$    $f(x)$  =A,$\underset{}{\lim}$    $g(x)$  =B.(条件：极限存在)极限里相加或相乘都等于极限f(x)相加减或相乘除极限g(x)，也等于A相加减或相乘除B。
### 第六节 极限存在准则 
- 准则一：数列{ ${x}_{n}$ },{ ${y}_{n}$ }
  -   $\exist$  ${n}_{0}$    $\in$  N,n>  ${n}_{0}$  时，  ${y}_{n}$    $\le$    ${x}_{n}$    $\le$    ${z}{n}$  .
  -   $\underset{n\rightarrow{\infty}}{\lim}$    ${y}_{n}$  =a, $\underset{n\rightarrow{\infty}}{\lim}$    ${z}_{n}$  =a,则  $\underset{n\rightarrow{\infty}}{\lim}$    ${x}_{n}$  =a。
  - g(x)  $\le$  f(x)  $\le$  h(x).
  -    $\underset{}{\lim}$  g(x)=A, $\underset{}{\lim}$  h(x)=A,则 $\underset{}{\lim}$  f(x)=A.  
- 洛必达法则：  $\underset{x\rightarrow{0}}{\lim}$     $\frac{f(x)}{g(x)}$  =  $\underset{x\rightarrow{0}}{\lim}$  其导数。
- $\underset{x\rightarrow{0}}{\lim}$    $\frac{sin(x)}{x}$  =1,有关于三角函数的求极限，要往  $\frac{sin(x)}{x}$  上转换。例如：  $\frac{tan(x)}{x}$  =  $\frac{sin(x)}{x}$  *  $\frac{1}{cos(x)}$.     