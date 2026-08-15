def twoSum(nums, target):
    seen = {}

    for i, num in enumerate(nums):
        diff = target - num

        if diff in seen:
            return [seen[diff], i]

        seen[num] = i

# Example
nums = [2, 7, 11, 15]
target = 9
print(twoSum(nums, target))



def fibonacci(n):
    if n <= 1:
        return n

    a = 0
    b = 1

    for _ in range(2, n + 1):
        a, b = b, a + b

    return b

# Example
print(fibonacci(10))


def maxSubArray(nums):
    current = maximum = nums[0]

    for num in nums[1:]:
        current = max(num, current + num)
        maximum = max(maximum, current)

    return maximum

# Example
nums = [-2,1,-3,4,-1,2,1,-5,4]
print(maxSubArray(nums))
