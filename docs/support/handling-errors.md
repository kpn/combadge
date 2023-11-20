# Handling errors

In **Pydantic** you can define a model as a [`#!python Union`](https://docs.python.org/3/library/typing.html#typing.Union) of possible models: whichever validates first – that one gets returned. For us, it means that you can simply `#!python Union[...]` all possible successful and error models – and use the `#!python Union` as a return type.

!!! tip "Discriminated unions"

    Consider using [discriminated unions](https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions) to define error models for different error codes.

In addition, Combadge provides some base response classes, which come in handy:

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
