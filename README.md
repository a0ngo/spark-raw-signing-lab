# SPARK'22 - Raw Signing Lab

## Overview
In this lab we will cover two main topics:
1. Proof of ownership - Standard Message signing and EIP712 signing
2. Adding support for an unsupported blockchain

This lab require at least basic coding skills with either python or javascript.<br>
Each lab is written in a diffrent programming language, however it is possible to write the code in a different programming language, the recommendation is to stick with python or javascript.<br>

## <span style="color:red">Security Advisory:</span>
Raw signing allows users to sign **any** arbitrary message.<br>
This feature is highly insecure as it can allow a malicious entity to trick a user into signing a message that is a valid transaction, and use it to steal funds.

When using Raw Signing, please follow the recommended practices for setting Raw Signing rule on the TAP (the lab does not follow these best practices due to it using testnet assets and not mainnet assets):
* Initiator is an Editor API user
* Source should be a specific Vault Account
* Set additional approvers (Action = Approved by)
* Set a human Designated Signer
* Specify a specific Asset type.

## Table of contents:
1. [Basic Lab](Basic.md#raw-signing-lab---basic)
2. [Advance Lab](Advance.md#raw-signing-lab---advance)
3. [Examples](#examples)

## Examples
Source code for both labs can be found here:<br>
- [Basic](examples/basic.js)
- [Advance](examples/advance.py)