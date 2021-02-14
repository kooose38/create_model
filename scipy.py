from scipy.stats import binom,poisson,geom,expon
#----------------------
#確率(p)をn回繰り返したときに、x回行った時の結果
n=np.arange(1,50) #nが大きくなるほど正規分布に等しくなる
data=binom.rvs(n=n,p=1/6,size=2160) #[0,0,0,1,0,2,3...]
#----------------------
#1hourに平均mu回起こる事象が、k回起こった時の確率
k=np.arange(0,100)
data=poisson.pmf(k=k,mu=30)
#----------------------
#確率(p)の事象が、k回目で初めて起きる確率
k=np.arange(1,51)
data=geom.pmf(k=k,p=1/6)
#----------------------
#1hourに平均scale回起こる事象が、x分までに起こる確率
x=np.arange(1,100)
data=expon.pdf(x=x,scale=60/10) #60分に10回起こる平均事象