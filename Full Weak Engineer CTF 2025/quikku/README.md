# quikku

## Description

ここで quikku

## Writeup

The implemented quicksort itself has no exploitable vulnerabilities, and even if we can control the elements being sorted, it is not possible to directly force the flag to appear as the minimum or maximum element.

The key observation is that each comparison incurs a delay of 0.0001 seconds. This means that if the number of comparisons during sorting is large, the result will take longer to compute, while if the number is small, the result will return quickly. It is well known that quicksort's number of comparisons can vary greatly depending on the input order and the sequence of pivots, ranging from an average of `O(n log n)` to a worst case of `O(n^2)`. Therefore, if we can construct an input that causes a significant difference in the number of comparisons depending on whether the flag is "before" or "after" it, we can determine the order of the flag via a timing attack.

Quicksort’s complexity is heavily dependent on pivot choice. If the pivot repeatedly splits the input roughly in half, the cost is small, but if the partitioning keeps skewing, the cost grows large.

To make reasoning clearer, we rewrite the setup as follows:

* Treat `ELAG` as value -2, and `GLAG` as value 101.
* Inputs are integers from 0 to 99.
* `FLAG` is either -1 (Pattern A) or 100 (Pattern B). The goal is to distinguish between these two cases.
    * We will attempt to make Pattern A run faster.
* From the input `[0, 1, …, 99]`, we generate the test sequence by swapping certain pairs of elements.
    * Since this quicksort chooses the middle element as pivot, already-sorted input is most efficient.
    * By modifying only those elements that will be chosen as pivots in Pattern B, we can worsen its performance while keeping Pattern A relatively efficient.

At initial state:

Pattern A:
```
idx    0   1   2   3   4   5 ... 102
[0]   -2  -1 101   0   1   2 ...  99
```

Pattern B:
```
idx    0   1   2   3   4   5 ... 102
[0]   -2 100 101   0   1   2 ...  99
```

The first pivot is always the 51st element, so it is difficult to create a big difference there. To amplify later effects, we want that pivot to be as small as possible. Swapping 48 and 0 achieves this, leading to deeper unbalanced recursion in both patterns and making the difference easier to detect.

Pattern A:

```
idx    0   1   2   3   4   5 ...  50  51  52 ... 102
[0]   -2  -1 101  48   1   2 ...  47   0  49 ...  99
[1] | -2  -1|  0|101  48   1 ...  46  47  49 ...  99|
```

Pattern B:

```
idx    0   1   2   3   4   5 ...  50  51  52 ... 102
[0]   -2 100 101  48   1   2 ...  47   0  49 ...  99
[1] | -2|  0|100 101  48   1 ...  46  47  49 ...  99|
```

The pivot in the right block is 50 in Pattern A and 49 in Pattern B. Next, we consider swapping 49 with the inefficient pivot value 1.

Pattern A(`49 ↔ 1`)

```
idx    0   1   2   3   4   5 ...  50  51  52  53  54 ... 102
[0]   -2  -1 101  48  49   2 ...  47   0   1  50  51 ...  99
[1] | -2  -1|  0|101  48  49 ...  46  47   1  50  51 ...  99|
[2] | -2| -1|  0| 48  49   2 ...  47   1| 50|101  51 ...  99|
```
(Used as pivot `50`)

Pattern B(`49 ↔ 1`)

```
idx    0   1   2   3   4   5 ...  50  51  52  53  54 ... 102
[0]   -2 100 101  48  49   2 ...  47   0   1  50  51 ...  99
[1] | -2|  0|100 101  48  49 ...  46  47   1  50  51 ...  99|
[2] | -2|  0|  1|100 101  48 ...  45  46  47  50  51 ...  99|
```

The next pivot in Pattern B is 50, but since it has already been used as a pivot in Pattern A, it cannot be swapped.
The same applies if we swap 49 with 2. However, if we swap 49 with 3:

Pattern A(`49 ↔ 3`)

```
idx    0   1   2   3   4   5 ...  50  51  52  53  54 ... 102
[0]   -2  -1 101  48   1   2 ...  47   0   3  50  51 ...  99
[1] | -2  -1|  0|101  48   1 ...  46  47   3  50  51 ...  99|
[2] | -2| -1|  0| 48   1   2 ...  47   3| 50|101  51 ...  99|
```
(Used as pivot `50`)

Pattern B(`49 ↔ 3`)

```
idx    0   1   2   3   4   5 ...  50  51  52  53  54 ... 102
[0]   -2 100 101  48   1   2 ...  47   0   3  50  51 ...  99
[1] | -2|  0|100 101  48   1 ...  46  47   3  50  51 ...  99|
[2] | -2|  0|  1   2|  3|100 ...  45  46  47  50  51 ...  99| 
```

The next pivot becomes 51, which can now be swapped. Let’s try swapping 51 with 4.

Pattern A(`51 ↔ 4`)

```
idx    0   1   2   3   4   5 ...  28  29  30 ...  50  51  52  53  54 ...  77  78  79 ... 102
[0]   -2  -1 101  48   1   2 ...  25  26  27 ...  47   0   3  50   4 ...  74  75  76 ...  99
[1] | -2  -1|  0|101  48   1 ...  24  25  26 ...  46  47   3  50   4 ...  74  75  76 ...  99|
[2] | -2| -1|  0| 48   1   2 ...  25  26  27 ...   3   4| 50|101  51 ...  74  75  76 ...  99|
[3] | -2| -1|  0|  1   2   5 ...   4| 25| 48 ...  46  47| 50| 51  52 ...| 75|101  76 ...  99|
```
(Used as pivot `25, 50, 75`)


Pattern B(`51 ↔ 4`)

```
idx    0   1   2   3   4   5   6 ...  50  51  52  53  54  55 ... 102
[0]   -2 100 101  48   1   2  49 ...  47   0   3  50   4  52 ...  99
[1] | -2|  0|100 101  48   1   2 ...  46  47   3  50   4  52 ...  99|
[2] | -2|  0|  1   2|  3|100 101 ...  45  46  47  50   4  52 ...  99| 
[3] | -2|  0|  1|  2|  3|  4|100 ...  44  45  46  47  50  52 ...  99|
```

The next pivot in Pattern B is 50, but since it has already been used in Pattern A, it cannot be swapped either. If we swap 51 ↔ 5: 

Pattern A(`51 ↔ 5`)

```
idx    0   1   2   3   4   5 ...  28  29  30 ...  50  51  52  53  54 ...  77  78  79 ... 102
[0]   -2  -1 101  48   1   2 ...  25  26  27 ...  47   0   3  50   5 ...  74  75  76 ...  99
[1] | -2  -1|  0|101  48   1 ...  24  25  26 ...  46  47   3  50   5 ...  74  75  76 ...  99|
[2] | -2| -1|  0| 48   1   2 ...  25  26  27 ...   3   5| 50|101  51 ...  74  75  76 ...  99|
[3] | -2| -1|  0|  1   2   4 ...   5| 25| 48 ...  46  47| 50| 51  52 ...| 75|101  76 ...  99|
```
(ピボットとして使用済み `25, 50, 75`)

Pattern B(`51 ↔ 5`)

```
idx    0   1   2   3   4   5   6   7 ...  50  51  52  53  54  55 ... 102
[0]   -2 100 101  48   1   2  49   4 ...  47   0   3  50   5  52 ...  99
[1] | -2|  0|100 101  48   1   2  49 ...  46  47   3  50   5  52 ...  99|
[2] | -2|  0|  1   2|  3|100 101  48 ...  45  46  47  50   5  52 ...  99| 
[3] | -2|  0|  1|  2|  3|  4|  5|100 ...  44  45  46  47  50  52 ...  99|
```

The next pivot in Pattern B is 52, and by repeating the similar process, we can continue in the same way. After going far enough, a pattern becomes apparent, and we can see that the input can be generated with the following code:

```python
pattern = list(range(100))
pattern[0], pattern[48] = pattern[48], pattern[0] 
pattern[3], pattern[49] = pattern[49], pattern[3] 
for i in range(15):
    pattern[2*i+5], pattern[i+51] = pattern[i+51], pattern[2*i+5]
```

Let's test how much difference occurs:

```python

def create_ans():
    pattern = list(range(100))
    pattern[0], pattern[48] = pattern[48], pattern[0] 
    pattern[3], pattern[49] = pattern[49], pattern[3] 
    for i in range(15):
        pattern[2*i+5], pattern[i+51] = pattern[i+51], pattern[2*i+5]
    return pattern


def test(pattern):
    count = 0
    def compare(a, b):
        nonlocal count
        count += 1
        if a < b:
            return -1
        elif a == b:
            return 0
        return 1


    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr)//2]
        left = []
        middle = []
        right = []
        for x in arr:
            val = compare(x, pivot)
            if val == -1:
                left.append(x)
            elif val == 0:
                middle.append(x)
            else:
                right.append(x)
        return quick_sort(left) + middle + quick_sort(right)
    quick_sort(pattern)
    return count


pattern = create_ans()
print("pattern A: ", pattern_a := test([-2, -1, 101] + pattern))
print("pattern B: ", pattern_b := test([-2,100, 101] + pattern))

print("time difference: ", (pattern_b - pattern_a)*0.0001)
```

Result:

```
pattern A:  871
pattern B:  2202
time difference:  0.1331
```

In other words, there is a difference of at least 132 ms, which is sufficient to detect reliably. After that, we generate a fake flag that produces the arrangement described above, use a timing attack to determine whether it corresponds to Pattern A or Pattern B, and then apply binary search to recover the actual flag.

## Flag

`fwectf{1m_7h3_qu1kk357_c7f_pl4y3r}`

