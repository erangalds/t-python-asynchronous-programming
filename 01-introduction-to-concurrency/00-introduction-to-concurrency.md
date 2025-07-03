# Introduction to Concurrency

I am going to talk about below points. 

+ What is Concurrency?
+ Concurrency vs Parallelism
+ Why Concurrency? (I/O bound, CPU bound tasks)
+ The Global Interpreter Lock (GIL) - A python specific challenge

## What is concurrency?

Concurrency refers to the ability of a program to handle multiple tasks *seemingly* at the *same time*. It's about dealing with *many things at once*. 

A very simple example: 

Imagine a chef in a kitchen. They might be chopping vegetables, while water boils on the stove, and a cake bakes in the oven. The chef isn't doing all these things _simultaneously_ (they only have two hands), but they _switch between them_ to ensure all tasks progress. This is concurrency.

## Concurrency vs Parallelism

+ **Concurrency**: Multiple tasks make progress over overlapping time periods, but not necessarily at the *exact same instant*. It's about *managing mutiple tasks*. Single Core. A Single chef juggling with multiple dishes. 
+ **Parallelism**: Multiple tasks truely execute at the *exact same instant* on different CPU cores or processors. It's about doing multiple things at once. Multi Core. Multiple chefs in the kitches, each working on a different dish simultaneously. 

## Why Concurrency? (I/O bound, CPU bound tasks)

Understanding the nature of the tasks is crucial for chosing the right concurrency model. 

### I/O Bound Tasks: 

These tasks spend most of their time waiting for input/output operations to complete. Examples: 

+ Network requests (fetching data from a website, calling an API)
+ Reading and writing from disks (files, databases)
+ User input when a program performs an I/O operation. The CPU typically waits idly. 

Concurrency allows the program to switch to another tasks during this waiting period, making better use of CPU time and improving overall throughput. 

### CPU Bound Tasks:

These tasks spend most of their time performing computations on the CPU. Examples: 

+ Heavy mathematical calculations: 
+ Image processing
+ Data Analysis (sorting, filtering large databases)

For CPU bound tasks, concurrency (especially multithreading in python) might not offer significant performance gains due to the GIL. Parallelism (multiprocessing) is usually the answer. 

## The Global Interpreter Lock (GIL) - A python specific challenge

This is a very interesting topic. The Global Interpreter Lock (GIL) is a mutex (mutual exclusion lock). What is does is, it protects access to python objects. What exactly did I mean by protecting access to python objects? Well, it prevents native threads from executing python bytecodes simultaneously in the CPython interpreter (the standard python implementation). 

What does it mean? Even if we run the python code on a multi-core maching, if you have a python program using multiple threads, only one thread can execute python bytecode at any given time. The other threads will wait for the GIL to be released. 

So how does the GIL impact the CPU bound tasks and I/O bound tasks? 

+ **CPU-bound tasks**: If you have a CPU-bound tasks which are purely computational, multithreading in python usually doesn't lead to any performance improvements and can even decrease performance due to the overhead of context switching between threads trying to acquire the GIL.
+ **I/O-bound tasks**: The GIL is released during I/O operations (like reading from a file, making a network request). This means that while one thread is waiting for an I/O operation to complete, another thread can acquire the GIL and execute python code. This is why multithreading can be beneficial for I/O-bound tasks in python. 

Is there a way to bypass the use of GIL?

### How to bypass the GIL?

+ **Multiprocessing**: Use separate processes, each with its own, python interpreter and thus its own GIL. This is true parallelism. 
+ **asyncio**: This is not parallelism. It's cooperative multitasking within a single thread, where tasks explicitly yield control when waiting for I/O. The GIL is not an issue here, because only one 'logial' tasks is executing python code at a time. 
+ **C Extensions**: Libraries written in C (like NumPY) can release the GIL during their computationally intensive parts, allowing true parallelism if used from multiple threads. 







