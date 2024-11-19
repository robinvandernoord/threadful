# Changelog

<!--next-version-placeholder-->

## v0.4.0 (2024-11-19)

### Feature

* **animate:** Add clear_with option to replace animation with a specific character once the thread is done ([`23d0460`](https://github.com/robinvandernoord/threadful/commit/23d0460d4e759be52541794ff5fbe411dfaa06b3))

### Fix

* **result:** Improve handling of callback functions in threading module to prevent unexpected behavior when starting threads after result retrieval ([`4a00b96`](https://github.com/robinvandernoord/threadful/commit/4a00b961c35dbf8250ed8dda7fe74565d7e3f3a3))

### Documentation

* Expanded examples ([`1f419c6`](https://github.com/robinvandernoord/threadful/commit/1f419c6d5f2248c7cd5914cfc3c3712578683db6))

## v0.3.0 (2024-03-11)

### Feature

* **animate:** Improved 'text' handling: now supports callback function ([`b8205c4`](https://github.com/robinvandernoord/threadful/commit/b8205c4d8834e195fe253545830738e5a7d89535))

## v0.2.2 (2024-02-29)

### Fix

* Add "text=..." option for animate() ([`29a9618`](https://github.com/robinvandernoord/threadful/commit/29a96180a373ad8172f5ae0d8311eb535505c8b5))

## v0.2.1 (2024-02-29)

### Fix

* Use thread.join() instead of thread.result().unwrap() to raise the right exception instead of UnwrapError ([`496b0ae`](https://github.com/robinvandernoord/threadful/commit/496b0ae09e42dff67805352d3d8de1e6b4d2b79d))

## v0.2.0 (2024-02-29)

### Feature

* New bonus feature 'animate' to show an animation while waiting for a thread ([`aba27f3`](https://github.com/robinvandernoord/threadful/commit/aba27f3a9d11b9ee6952d04c6bdce93daaefc286))

## v0.1.1 (2024-01-31)

### Documentation

* Added examples with `.catch()` ([`61647ef`](https://github.com/robinvandernoord/threadful/commit/61647efa7d78fafd4b2531d2410f51c81b5e9a3a))

## v0.1.0 (2024-01-31)

### Feature

* Implemented all basic features for 0.1 ([`f591383`](https://github.com/robinvandernoord/threadful/commit/f59138321fbd7b0740984b3fb00031676af9a687))
* WIP, copied thread code from 2fas ([`662d7e5`](https://github.com/robinvandernoord/threadful/commit/662d7e52ba9219d0a3683312c08f6d9ed8fc552e))
