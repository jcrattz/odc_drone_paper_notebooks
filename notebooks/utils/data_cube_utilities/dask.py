import os
import psutil
import numpy as np
import dask
from datacube.utils.dask import start_local_dask
from datacube.utils.rio import configure_s3_access

def create_local_dask_cluster(spare_mem='3Gb',
                              aws_unsigned= True,
                              display_client=True,
                              start_local_dask_kwargs=None,
                              configure_s3_access_kwargs=None):
    """
    Credit belongs to Digital Earth Africa:
    https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/master/Scripts/deafrica_dask.py
    
    Using the datacube utils function 'start_local_dask', generate
    a local dask cluster.
    
    Example use :
        
        import sys
        sys.path.append("../Scripts")
        from deafrica_dask import create_local_dask_cluster
        
        create_local_dask_cluster(spare_mem='4Gb')
    
    Parameters
    ----------  
    spare_mem : String, optional
        The amount of memory, in Gb, to leave for the notebook to run.
        This memory will not be used by the cluster. e.g '3Gb'
    aws_unsigned : Bool, optional
         This parameter determines if credentials for S3 access are required and
         passes them on to processing threads, either local or on dask cluster. 
         Set to True if working with publicly available datasets, and False if
         working with private data. i.e if loading Landsat C2 provisional data set 
         this to aws_unsigned=False
    display_client : Bool, optional
        An optional boolean indicating whether to display a summary of
        the dask client, including a link to monitor progress of the
        analysis. Set to False to hide this display.
    start_local_dask_kwargs: dict, optional
        Keyword arguments for the function `datacube.utils.dask.start_local_dask`, which
        creates the Dask client.
        Some settings to configure include the number of workers, number of threads per worker, and the memory limit.
    configure_s3_access_kwargs: dict, optional
        Keyword arguments for the function `datacube.utils.rio.configure_s3_access`, which
        configures the Dask to access S3.
    """
    start_local_dask_kwargs = {} if start_local_dask_kwargs is None else start_local_dask_kwargs
    configure_s3_access_kwargs = {} if configure_s3_access_kwargs is None else configure_s3_access_kwargs
    
    # configure dashboard link to go over proxy
    dask.config.set({"distributed.dashboard.link":
                 os.environ.get('JUPYTERHUB_SERVICE_PREFIX', '/')+"proxy/{port}/status"})

    # start up a local cluster
    num_physical_cpu = psutil.cpu_count(logical=False)
    num_logical_cpu = psutil.cpu_count(logical=True)
    start_local_dask_kwargs.setdefault('n_workers', 1)
    start_local_dask_kwargs.setdefault('threads_per_worker', int(np.floor(num_logical_cpu/start_local_dask_kwargs['n_workers'])))
    client = start_local_dask(mem_safety_margin=spare_mem, **start_local_dask_kwargs)

    ## Configure GDAL for s3 access
    configure_s3_access(aws_unsigned=aws_unsigned,  
                        client=client, **configure_s3_access_kwargs)

    return client