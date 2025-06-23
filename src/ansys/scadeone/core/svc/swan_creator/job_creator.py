# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import Union
from ansys.scadeone.core.common.storage import JobStorage
from ansys.scadeone.core.interfaces import IProject
from ansys.scadeone.core.job import CodeGenerationJob, Job, JobType, SimulationJob, TestExecutionJob


class JobFactory:
    """Factory used to create the Job type corresponding to the given JobStorage"""

    def __new__(cls, *args, **kwargs) -> "JobFactory":
        if not cls._instance:
            cls._instance = super(JobFactory, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_job(job_storage: JobStorage, sproj: IProject) -> Union[Job, None]:
        """Create a Job derivated object from a JobStorage and a project

        Parameters
        ----------
        job_storage : JobStorage
            Job storage
        sproj : Project
            Corresponding project

        Returns
        -------
        Job
            The new Job derivated object
        """
        json = job_storage.json
        name = json["Properties"]["Name"]
        job = None
        if json["Kind"] == str(JobType.CODEGEN):
            job = CodeGenerationJob(name, sproj, json, job_storage)
        elif json["Kind"] == str(JobType.SIMU):
            job = SimulationJob(name, sproj, json, job_storage)
        elif json["Kind"] == str(JobType.TESTEXEC):
            job = TestExecutionJob(name, sproj, json, job_storage)
        return job

    @staticmethod
    def new_job(kind: JobType, name: str, sproj: IProject) -> "Job":
        """Create a job from scratch

        Parameters
        ----------
        kind : JobType
            New job kind
        name : str
            New job name
        sproj : Project
            Corresponding Project. Necessary to determine sjob save location

        Returns
        -------
        Job
            Created job

        Raises
        ------
        ScadeOneException
            No valid job kind provided
        """
        if kind == JobType.CODEGEN:
            job = CodeGenerationJob(name, sproj)
        elif kind == JobType.SIMU:
            job = SimulationJob(name, sproj)
        elif kind == JobType.TESTEXEC:
            job = TestExecutionJob(name, sproj)
        else:
            from ansys.scadeone.core import ScadeOneException

            raise ScadeOneException("A valid job type must be provided at creation.")
        return job
