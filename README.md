# Python Asynchronous Programming and Concurrency Handling

Python offers several ways to handle concurrency, and it's vital to understand their differences and when to use each. This is a topic which I was curious for many years, but didn't have time, no a requirement to learn what it is. Looks like time has come, so I had a quick look at what it is and as usual, I thought to share what I learned with you. I am going to share below topics with you which I learnt during my exploration about this topic. 

## Table of Contents

+ [Introduction to Concurrency](./01-introduction-to-concurrency/00-introduction-to-concurrency.md)
+ [Multithreading](./02-multithreading/00-multithreading-in-python.md)
+ [Asynchronous Programming](./03-asynchronous-programming/00-asynchronous-programming.md)
+ [Multiprocessing](./04-multiprocessing/00-multiprocessing.md)
+ [Concurrent Futures](./05-concurrent-futures/00-concurrent-futures.md)
+ [Decision Guide](./06-decision-guide/00-decision-guide.md)
+ [Advanced Topics and Best Practices](./07-advanced-topics/00-advanced-topics.md)

## Setting up the environment for the lab

I think it would be cleaner and easier if you create a separate python environment for this lab. Even though we use the standard modules, (we need `requests` module separate installed for some demos). 

So let me show you to create a separate python environment using anaconda. 

```bash
# Create a new environment
conda create --name l-asyncio python=3.12
# Verify whether the environment is created
conda env list
# Activate the environment
conda activate l-asyncio
# Install the requests module
python -m pip install requests # Or else you can use -> conda install requests
```

Each topic has example code, and the example code is placed under the respective directories. Enjoy the lab! 




