# Cache Timing

There are two duration values that need to be understood when configuring a
cache in NGINX.

## Backend Response Validity

The `proxy_cache_valid` directive specifies how long a backend response will be
considered valid by the cache. Responses that are considered valid will be
served from the cache without any further requests to the backend.

After this time expires, the cached response will be considered *stale* and
either won't be served (triggering a new backend request) or will continue to
be served depending on whether the `proxy_cache_use_stale` setting is used.

Read more about `proxy_cache_valid` in the
[documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_valid).

## Cache Item Inactivity

The `inactive` argument for the `proxy_cache_path` directive specifies how long
a cached response will be stored in the cache *after its last use*.

(Note that even stale responses will be considered recently used if there are
requests to them.)

Read more about `inactive` in the `proxy_cache_path`
[documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_path).

# Links

* [NGINX http_proxy module documentation](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
* [NGINX configuration file measurement units](http://nginx.org/en/docs/syntax.html)
