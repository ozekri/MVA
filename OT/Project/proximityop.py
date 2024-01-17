import numpy as np
import matplotlib.pyplot as plt
from proxop import AbsValue
import numpy as np

abso = AbsValue()
x = np.linspace(-5,5,300)


plt.figure(1,figsize=(15,8))
plt.subplot(1,2,1)
plt.plot(x,abso.prox(x,gamma=0.5),c='blue',label=r"$\text{prox}_{\gamma\mid \cdot \mid}, \gamma= 0.5$")
plt.plot(x,x,'--',c='black',label=r"$\text{I}_d$")
plt.xlim(-3,3)
plt.ylim(-2,2)
plt.legend(fontsize="20")


plt.subplot(1,2,2)
plt.plot(x,np.abs(abso.prox(x,gamma=0.5)) + 0.25*np.abs(abso.prox(x,gamma=0.5)-x)**2,c='blue',label=r"$\gamma_{\mid \cdot \mid}, \gamma= 0.5$")
plt.plot(x,np.abs(x),'--',c='black',label=r"$\mid \cdot \mid$")
plt.xlim(-3,3)
plt.ylim(-2,2)
plt.legend(fontsize="20")
plt.show()