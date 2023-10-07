from mpi4py import MPI
import random

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

def merge(arr, temp):
    n = len(arr)
    mid = n // 2
    i = 0
    j = mid
    k = 0

    while i < mid and j < n:
        if arr[i] < arr[j]:
            temp[k] = arr[i]
            i += 1
        else:
            temp[k] = arr[j]
            j += 1
        k += 1

    while i < mid:
        temp[k] = arr[i]
        i += 1
        k += 1

    while j < n:
        temp[k] = arr[j]
        j += 1
        k += 1

    for i in range(n):
        arr[i] = temp[i]

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        # Generate a random unsorted array
        array_size = 10
        unsorted_array = [random.randint(1, 100) for _ in range(array_size)]
        print("Unsorted Array:", unsorted_array)
    else:
        unsorted_array = None

    # Broadcast the unsorted array to all processes
    unsorted_array = comm.bcast(unsorted_array, root=0)

    # Calculate the local portion to sort
    local_size = len(unsorted_array) // size
    local_start = rank * local_size
    local_end = local_start + local_size

    # Sort the local portion using bubble sort
    local_array = unsorted_array[local_start:local_end]
    bubble_sort(local_array)

    # Gather all sorted local portions to the root process
    sorted_array = comm.gather(local_array, root=0)

    if rank == 0:
        # Merge the sorted sub-arrays to get the final sorted array
        temp_array = [0] * array_size
        while len(sorted_array) > 1:
            merge(sorted_array[0], temp_array)
            merge(sorted_array[1], temp_array)
            sorted_array.pop(0)
            sorted_array.pop(0)
            sorted_array.append(temp_array.copy())
        final_sorted_array = sorted_array[0]

        print("Sorted Array:", final_sorted_array)
