mental_poker
============
Implementation of fast mental poker protocol proposed in

    SECURE AND PRACTICAL CONSTANT ROUND MENTAL POKER TZER-JEN WEI (2013)
    COMMUNICATION EFFICIENT SHUFFLE FOR MENTAL POKER PROTOCOLS TZER-JEN WEI  (2011)
    Fast Mental Poker (2010)

( http://weijr-eng.blogspot.tw/2014/06/some-of-my-draft-papers-on-mental-poker.html )

These implementations are used to estimate the computation cost of the mental poker protocols. 
The coding style is a bit strange, because I want to python code to be as similar as the pseudo code presented in the paper as possible AND I dont want to use any advaced techeniques or magic to do that.

I should have choosed Python 3 which has better coroutine support than Python 2.
Unfoirtunenately, I didn't. 
Therefore, the result is kind of ugly, function and inner functions kind of looks like classes witout explicit self, or modules with initialize parameter.

