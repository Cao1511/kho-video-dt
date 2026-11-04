#!/usr/bin/env python3
"""Nap cache ca web mayducthanh.vn (nha mang tat crawler LiteSpeed -> tu lam).
Chay boi workflow nap-cache.yml moi 30 phut (nguoi dung dong y 04/11/2026).
Chi mo trang nhu khach (dang nen gzip cho nhe bang thong), khong sua/xoa gi."""
import json, time, gzip, urllib.request, concurrent.futures as cf

SITE = "https://mayducthanh.vn"
UA = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Mobile Safari/537.36 DucThanh-NapCache"


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
        return r.status, r.headers.get("x-litespeed-cache", "-"), time.time() - t, body


def jget(path):
    try:
        return json.loads(get(SITE + path)[3])
    except Exception as e:
        print("loi", path, e); return []


def main():
    urls = {SITE + "/"}
    for pg in range(1, 6):
        a = jget(f"/wp-json/wc/store/v1/products?per_page=100&page={pg}")
        if not isinstance(a, list) or not a:
            break
        urls |= {x["permalink"] for x in a}
    urls |= {c["permalink"] for c in jget("/wp-json/wc/store/v1/products/categories?per_page=100") if isinstance(c, dict) and c.get("permalink")}
    urls |= {p["link"] for p in jget("/wp-json/wp/v2/pages?per_page=50&_fields=link") if isinstance(p, dict)}
    urls |= {p["link"] for p in jget("/wp-json/wp/v2/posts?per_page=50&_fields=link") if isinstance(p, dict)}

    def one(u):
        try:
            st, h, dt, _ = get(u)
            return u, st, h, dt
        except Exception as e:
            return u, "loi", str(e)[:60], 0

    with cf.ThreadPoolExecutor(3) as ex:
        res = list(ex.map(one, sorted(urls)))
    miss = [r for r in res if not str(r[2]).startswith("hit")]
    print(f"Tong {len(res)} trang | da co cache {len(res)-len(miss)} | vua nap {len(miss)}")
    for u, st, h, dt in miss:
        print(f"  nap: {u.replace(SITE,'')} {st} {h} {dt:.1f}s")


if __name__ == "__main__":
    main()
