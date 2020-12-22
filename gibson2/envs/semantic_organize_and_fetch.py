from gibson2.envs.igibson_env import iGibsonEnv
from gibson2.objects.articulated_object import ArticulatedObject
from gibson2.objects.custom_articulated_object import CustomArticulatedObject
from gibson2.utils.custom_utils import ObjectConfig
from gibson2.tasks.semantic_rearrangement_task import SemanticRearrangementTask
import numpy as np


class SemanticOrganizeAndFetch(iGibsonEnv):
    """
    This class corresponds to a reward-free semantic organize-and-fetch task, where the goal is to either sort objects
    from a pile and place them in semantically-meaningful locations, or to search for these objects and bring them
    to a specified goal location

    Args:
        config_file (str): config_file path
        object_configs (ObjectConfig or list of ObjectConfig): Object(s) to use for this task
        task_mode (str): Take mode for this environment. Options are "organize" or "fetch"
        scene_id (str): override scene_id in config file
        mode (str): headless, gui, iggui
        action_timestep (float): environment executes action per action_timestep second
        physics_timestep (float): physics timestep for pybullet
        device_idx (int): which GPU to run the simulation and rendering on
        render_to_tensor (bool): whether to render directly to pytorch tensors
        automatic_reset (bool): whether to automatic reset after an episode finishes
    """
    def __init__(
        self,
        config_file,
        object_configs,
        task_mode="organize",
        scene_id=None,
        mode='headless',
        action_timestep=1 / 10.0,
        physics_timestep=1 / 240.0,
        device_idx=0,
        render_to_tensor=False,
        automatic_reset=False,
    ):
        # Store objects
        self.object_configs = [object_configs] if isinstance(object_configs, ObjectConfig) else object_configs
        self.objects = None                     # to be filled later during load() - maps names to object classes

        # Store other internal variables
        self.task = None
        self.task_mode = task_mode

        # Run super init
        super().__init__(
            config_file=config_file,
            scene_id=scene_id,
            mode=mode,
            action_timestep=action_timestep,
            physics_timestep=physics_timestep,
            device_idx=device_idx,
            render_to_tensor=render_to_tensor,
            automatic_reset=automatic_reset,
        )

    def load(self):
        """
        Load environment
        """
        # Make sure "task" in config isn't filled in, since we write directly to it here
        assert "task" not in self.config, "Task type is already pre-determined for this env," \
                                          "please remove key from config file!"
        self.config["task"] = "semantic_rearrangement"

        # Run super call
        super().load()

        # Load objects into env
        self.objects = {}
        for object_config in self.object_configs:
            obj = CustomArticulatedObject(**object_config._asdict())
            # Import this object into the simulator
            self.simulator.import_object(obj=obj, class_id=obj.class_id)
            # Add this object to our dict of objects
            self.objects[obj.name] = obj

        # Load task
        self.task = SemanticRearrangementTask(
            env=self,
            objects=list(self.objects.values()),
            goal_pos=[0, 0, 0],
            randomize_initial_robot_pos=(self.task_mode == "fetch"),
        )

