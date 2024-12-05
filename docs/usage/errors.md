# Errors

In Combadge, models are responsible for parsing of errors: one can define a response model as a [`#!python Union`](https://docs.python.org/3/library/typing.html#typing.Union) of possible models, _including error models_. Whatever model validates first – gets returned.

!!! tip "Discriminated unions"

    Consider using [discriminated unions](https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions) to define error models for different error codes.

But in order to make it simpler, Combadge provides some base response classes, which come in handy:

::: combadge.core.response.BaseResponse
    options:
      show_root_heading: true
      heading_level: 2

!!! tip "That looks rusty, huh"

    The resemblance with Rust is not concidential: the author was inspired by [`std::result::Result`](https://doc.rust-lang.org/std/result/enum.Result.html).

<br>

::: combadge.core.response.SuccessfulResponse
    options:
      show_root_heading: true
      heading_level: 2

<br>

::: combadge.core.response.ErrorResponse
    options:
      show_root_heading: true
      heading_level: 2
      members: ["Error", "raise_for_result", "unwrap"]

<br>

::: combadge.core.errors
    options:
      heading_level: 2
