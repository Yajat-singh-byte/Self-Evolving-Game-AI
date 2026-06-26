# Self Evolving Genetic AI Enemy

An experimental game AI that learns through genetic evolution instead of scripted behavior.

The project uses a custom Recurrent Neural Network (RNN) combined with mutation based evolution. After every round, the best performing neural network is saved while new generations are created by mutating the previous best model. Over time, the AI gradually improves its movement and survival strategy.

## Features

* Custom Recurrent Neural Network implementation
* Genetic mutation based evolution
* Persistent learning through saved neural network weights
* Real time training inside the game
* Fitness based model selection
* No machine learning frameworks used
* Built entirely in Python

## How It Works

Each generation plays a combat round against the player.

The AI receives information about the environment including player position, distance, wall proximity, nearby bullets, previous actions, and health.

At the end of every round a fitness score is calculated. If the current model performs better than the previous best, its weights are saved. The next generation starts from the best model with random mutations applied, allowing the AI to continuously improve over time.

## Neural Network

Architecture

```
16 Inputs
    ↓
32 Hidden Units
    ↓
Recurrent Hidden State
    ↓
2 Outputs
```

Outputs

* Horizontal movement
* Vertical movement

## Technologies

* Python
* NumPy
* Pygame

## Purpose

This project was created to explore how lightweight neural networks and genetic evolution can produce adaptive game AI without using reinforcement learning libraries or pretrained models.

It serves as an experiment in AI programming, game development, and evolutionary algorithms.
