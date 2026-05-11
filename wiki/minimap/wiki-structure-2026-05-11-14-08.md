# Wiki Structure

- Overview
  type: overview
  purpose: Explain what minimap is - a vision-based Genshin Impact automation tool that uses minimap recognition to automate gameplay tasks.
  answers:
    - What is this tool and what can it automate?
    - What are the main capabilities (collection, fighting, domain running, daily missions)?
    - What are the prerequisites and runtime requirements?
  source_hints:
    - myrepo/minimap/README.md
    - myrepo/minimap/requirements.txt
    - myrepo/minimap/config-template.yaml

- Architecture
  type: architecture
  purpose: Explain the layered architecture with vision capture, position tracking, controllers, and path execution.
  answers:
    - What are the major architectural layers?
    - How does screen capture feed into position tracking?
    - How do controllers orchestrate different automation tasks?
  source_hints:
    - myrepo/minimap/capture/
    - myrepo/minimap/matchmap/
    - myrepo/minimap/controller/
    - myrepo/minimap/myexecutor/
  children:
    - Vision Capture Layer
      type: subsystem
      purpose: Explain how screen capture and UI element recognition work.
      answers:
        - How does the system capture game screenshots?
        - How are UI icons and templates recognized?
        - How does the system detect game state (flying, swimming, climbing)?
      source_hints:
        - myrepo/minimap/capture/capture_factory.py
        - myrepo/minimap/capture/recognizable_capture.py
        - myrepo/minimap/capture/genshin_capture.py
        - myrepo/minimap/resources/template/
    - Position Tracking Layer
      type: subsystem
      purpose: Explain how minimap matching determines player position and rotation.
      answers:
        - How does SIFT feature matching locate the player on the map?
        - How is rotation (camera direction) calculated?
        - How does local vs global map matching work?
      source_hints:
        - myrepo/minimap/matchmap/minimap_interface.py
        - myrepo/minimap/matchmap/camera_orientation.py
        - myrepo/minimap/matchmap/sifttest/
    - Controller Layer
      type: subsystem
      purpose: Explain how controllers orchestrate different automation domains.
      answers:
        - What is the BaseController and what capabilities does it provide?
        - How do specialized controllers (Fight, Map, Domain, Dialog) extend the base?
        - How do controllers interact with the vision layer?
      source_hints:
        - myrepo/minimap/controller/BaseController.py
        - myrepo/minimap/controller/FightController.py
        - myrepo/minimap/controller/MapController2.py
        - myrepo/minimap/controller/DomainController.py
    - Path Execution Layer
      type: subsystem
      purpose: Explain how the system navigates from point to point along predefined paths.
      answers:
        - How are paths defined and loaded from JSON files?
        - How does the executor move toward waypoints and handle stuck situations?
        - How are position mutations (death teleport) detected and handled?
      source_hints:
        - myrepo/minimap/myexecutor/BasePathExecutor2.py
        - myrepo/minimap/myexecutor/CollectPathExecutor.py
        - myrepo/minimap/myexecutor/FightPathExecutor.py

- Runtime Flow
  type: lifecycle
  purpose: Explain the execution flow from server request to automation completion.
  answers:
    - How does an HTTP request trigger an automation task?
    - How does the server validate and route requests?
    - How does the execution thread coordinate capture, tracking, and movement?
  source_hints:
    - myrepo/minimap/server/MiniMapServer.py
    - myrepo/minimap/server/ServerAPI.py
    - myrepo/minimap/server/service/

- Automation Workflows
  type: workflow
  purpose: Explain the different automation workflows supported by the system.
  answers:
    - What automation tasks are available?
    - How is each workflow structured and configured?
    - What are the failure handling strategies for each workflow?
  source_hints:
    - myrepo/minimap/server/controller/
    - myrepo/minimap/myexecutor/
  children:
    - Collection Workflow
      type: workflow
      purpose: Explain how material collection routes are executed.
      answers:
        - How are collection paths defined?
        - How does auto-pickup (crazy F) work near targets?
        - How are collection path files organized?
      source_hints:
        - myrepo/minimap/myexecutor/CollectPathExecutor.py
    - Domain Running Workflow
      type: workflow
      purpose: Explain how domain (秘境) automation runs from entrance to reward claim.
      answers:
        - How does the system navigate inside domains using YOLO tree detection?
        - How is the fight triggered and monitored?
        - How are rewards claimed with resin management?
      source_hints:
        - myrepo/minimap/controller/DomainController.py
        - myrepo/minimap/server/controller/ServerDomainController.py
        - myrepo/minimap/resources/model/bgi_tree.onnx
    - Daily Mission Workflow
      type: workflow
      purpose: Explain how daily commissions are automated.
      answers:
        - How are daily missions detected and navigated?
        - How are different mission types (combat, destroy pillars) handled?
        - How is the Katheryne reward collection integrated?
      source_hints:
        - myrepo/minimap/myexecutor/DailyMissionPathExecutor.py
        - myrepo/minimap/server/service/DailyMissionService.py
    - Ley Line Outcrop Workflow
      type: workflow
      purpose: Explain how ley line (地脉) challenges are automated.
      answers:
        - How are ley line types (exp/mora) selected?
        - How is the challenge started and completed?
        - How is the Kazuha pickup skill used for material collection?
      source_hints:
        - myrepo/minimap/myexecutor/LeyLineOutcropPathExecutor.py
        - myrepo/minimap/server/service/LeyLineOutcropService.py

- Fight System
  type: subsystem
  purpose: Explain the fight automation architecture with team-based skill sequences.
  answers:
    - How are fight teams configured with skill sequences?
    - How does the system switch characters and execute skills?
    - How are shield skills and mining skills handled specially?
    - How is combat exit detected?
  source_hints:
    - myrepo/minimap/controller/FightController.py
    - myrepo/minimap/fightmapper/BaseFightMapper.py
    - myrepo/minimap/fightmapper/FightMapperImpl.py

- Configuration System
  type: configuration
  purpose: Explain how the system is configured for different use cases.
  answers:
    - What configuration files exist and what do they control?
    - How are path executor parameters tuned (timeout, stuck thresholds)?
    - How are fight teams and domain mappings configured?
  source_hints:
    - myrepo/minimap/config-template.yaml
    - myrepo/minimap/myutils/configutils.py
    - myrepo/minimap/account-template.yaml

- HTTP API Surface
  type: api
  purpose: Document the HTTP API endpoints for triggering automation.
  answers:
    - What API endpoints are available?
    - How are requests structured and validated?
    - How does the server respond with status updates?
  source_hints:
    - myrepo/minimap/server/ServerAPI.py
    - myrepo/minimap/server/controller/
    - myrepo/minimap/server/dto/DataClass.py

- Development Setup
  type: development
  purpose: Explain how to set up the development environment and extend the system.
  answers:
    - How is the Python environment configured with dependencies?
    - How are OCR and YOLO models set up?
    - How are submodule resources (map data, GUI) managed?
    - How can new paths be created?
  source_hints:
    - myrepo/minimap/README.md
    - myrepo/minimap/requirements.txt
    - myrepo/minimap/myutils/kp_gen.py
    - myrepo/minimap/myexecutor/PathRecorderManually.py

- Extension Points
  type: extension
  purpose: Explain where the system can be extended with new functionality.
  answers:
    - How can new path executor types be added?
    - How can new fight skills be mapped?
    - How can new UI templates be added for recognition?
    - How can new automation workflows be integrated?
  source_hints:
    - myrepo/minimap/myexecutor/BasePathExecutor2.py
    - myrepo/minimap/fightmapper/BaseFightMapper.py
    - myrepo/minimap/capture/recognizable_capture.py
    - myrepo/minimap/resources/template/

- Error Handling & Recovery
  type: concept
  purpose: Explain how the system handles errors and recovers from failure states.
  answers:
    - How are stuck situations detected and recovered?
    - How is character death handled (food revive vs teleport revive)?
    - How are position mutations (teleport) detected and path adjusted?
    - How are dialog interruptions skipped?
  source_hints:
    - myrepo/minimap/myexecutor/BasePathExecutor2.py (MovingStuckException, MovingPositionMutationException)
    - myrepo/minimap/controller/DialogController.py
    - myrepo/minimap/controller/FightController.py (CharacterDieException)

- Logging & Debugging
  type: development
  purpose: Explain the logging system and debugging capabilities.
  answers:
    - How is the custom logger configured?
    - How can debug mode be enabled for visualization?
    - How does the path viewer help debug navigation?
  source_hints:
    - myrepo/minimap/mylogger/MyLogger3.py
    - myrepo/minimap/myexecutor/KeyPointViewer.py
    - myrepo/minimap/config-template.yaml (debug_enable)