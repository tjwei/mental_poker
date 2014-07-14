mental_poker
============
Implementation of fast mental poker protocol proposed in

    SECURE AND PRACTICAL CONSTANT ROUND MENTAL POKER TZER-JEN WEI (2013)
    COMMUNICATION EFFICIENT SHUFFLE FOR MENTAL POKER PROTOCOLS TZER-JEN WEI  (2011)
    Fast Mental Poker (2010)

( http://weijr-eng.blogspot.tw/2014/06/some-of-my-draft-papers-on-mental-poker.html )



These implementations are used to estimate the computation cost of the mental poker protocols. 
The coding style is a bit strange, because I want to python code to be as similar as the pseudo code presented in the paper as possible AND I dont want to use any advaced techeniques or magic to do that.

I should have chosen Python 3 which has better coroutine support than Python 2.
Unfoirtunenately, I didn't. 
Therefore, the result is kind of ugly, function and inner functions kind of looks like classes witout explicit self, or modules with initialize parameter.

Usage:

To simulate the protocol presented in the 2013 paper, 
````
python newp.py
````

To simulate the mcrp(Modified Castellà-Roca's Protocol see above papers), 
````
python mcrp.py
````
The following is the abstract of the 2013 paper:
We present a new mental poker protocol, which achieves negligible probability of cheating in constant round. All of previous secure mental poker protocol use L -round zero-knowledge protocols to ensure the probability of successful active cheating to be $O\left(2^{-L}\right)$ . 

Our protocol uses a different way to verify the integrity of the shuffle. The cryptosystem and the basic structure of our protocol is based on Castellà-Roca's mental protocol, which is very efficient and secure. The L-round zero-knowledge shuffle verification is replaced by a checksum-like framework. There are two kinds of checksums used in our shuffle: linear checksum and double exponentiation. The “linear checksum” is used to make sure that every card in the deck is distinct. The “double exponentiation checksum” is used to make sure that every card has a legitimate face value. 

The security can be proved under DDH assumption. The probability of successful cheating is negligible, even if the adversary can actively corrupt the majority of players. It is also very fast. For a 9 player game, the computation cost of our shuffle is comparable to the L
 -round verification with L=4. The time complexity of our shuffle is $\Theta\left(MN+N^{2}\right)E$
 (compares to $\Theta\left(MN^{2}L\right)E$
  for a L -round shuffle), where N
  is the number of players, M
  is the number of cards, and E
  is the computation cost of one modular exponentiation.

The communication cost is also reduced. Compares to the L-round protocol we based on , number of messages is reduced from $\Theta\left(N^{3}L\right)  to \Theta\left(N^{2}\right)$, and the total length of messages is reduced from $\Theta\left(N^{2}L\left(M+N\right)\right)\eta$  to $\Theta\left(MN^{2}\right)\eta$, where \eta
  is the length of an encryption key. For a 9-player game, our shuffle requires only 53\%  messages, and total length of messages is only 7\%
 (compares to the case L=30  and all L  rounds of shuffle verification are allowed to run in parallel).

It is the first constant round mental poker protocol that is provably secure and efficient enough to satisfy the practical needs. The probability of successful cheating is negligible, 
