# Wiki Structure

- Overview
  type: overview
  purpose: Explain what Minimap is, its capabilities, and the problems it solves for Genshin Impact automation.
  answers:
    - What is this system and what does it automate?
    - What are the main automation capabilities (collection, combat, missions)?
    - What are the system requirements and dependencies?
    - How do users interact with the system?
  source_hints:
    - README.md
    - config-template.yaml
    - requirements.txt
  children:
    - Quick Start
      type: workflow
      purpose: Guide users through the minimal steps to get Minimap running.
      answers:
        - How do I install and run the system?
        - What are the required game settings (resolution, frame rate)?
        - How do I configure accounts and paths?
      source_hints:
        - README.md (运行方式 section)
        - config-template.yaml
        - server/MiniMapServer.py

- Architecture
  type: architecture
  purpose: Explain the major components and their cooperation in the automation pipeline.
  answers:
    - What are the main architectural layers?
    - How do components interact from capture to execution?
    - What is the flow from screenshot to automated action?
    - Which components own which responsibilities?
  source_hints:
    - capture/
    - controller/
    - matchmap/
    - myexecutor/
    - server/
    - fightmapper/
  children:
    - Runtime Flow
      type: lifecycle
      purpose: Explain the main execution path through the system during automation.
      answers:
        - How does a task get executed from start to finish?
        - What starts the automation flow?
        - How does position tracking drive movement decisions?
        - Where are the key handoff points between components?
      source_hints:
        - myexecutor/BasePathExecutor2.py
        - server/service/TodoService.py
        - server/service/OneDragonService.py
    - Server Architecture
      type: subsystem
      purpose: Explain the Flask server structure, API endpoints, and real-time communication.
      answers:
        - How is the web server organized?
        - What API endpoints are available?
        - How does SocketIO enable real-time updates?
        - How do controllers map to services?
      source_hints:
        - server/MiniMapServer.py
        - server/controller/*.py
        - server/service/*.py

- Screen Capture System
  type: subsystem
  purpose: Explain how the system captures game window screenshots and processes them for recognition.
  answers:
    - How does window capture work?
    - How is the Genshin Impact window identified and tracked?
    - What capture methods are available (Win32 API, MSS)?
    - How are screenshots converted for processing?
  source_hints:
    - capture/windowcapture3.py
    - capture/capture_factory.py
    - capture/observable_capture.py
  children:
    - Template Recognition
      type: concept
      purpose: Explain how UI elements are detected via template matching.
      answers:
        - How are in-game UI elements recognized?
        - What templates are used for button detection?
        - How is screen position translated to game coordinates?
      source_hints:
        - capture/recognizable_capture.py
        - myutils/template_match_utils.py
        - resources/template/

- Minimap Position Tracking
  type: subsystem
  purpose: Explain the core positioning system that enables automated navigation.
  answers:
    - How does the system determine player position from the minimap?
    - What is SIFT matching and how is it used?
    - How is rotation/direction detected?
    - How are local and global maps coordinated?
  source_hints:
    - matchmap/minimap_interface.py
    - matchmap/sifttest/
    - server/service/MinimapService.py
  children:
    - Map Matching Algorithm
      type: concept
      purpose: Explain the technical details of position determination via feature matching.
      answers:
        - How does SIFT feature matching work for minimap localization?
        - How is global vs local matching coordinated?
        - What determines matching accuracy and speed?
        - How is the map scale factor handled?
      source_hints:
        - matchmap/sifttest/sifttest5.py
        - matchmap/sifttest/sifttest6.py
        - myutils/sift_utils.py
    - Rotation Detection
      type: concept
      purpose: Explain how player camera direction is determined.
      answers:
        - How is the viewing angle/rotation calculated?
        - What visual cues are used for direction detection?
        - How accurate is rotation tracking?
      source_hints:
        - matchmap/camera_orientation.py
        - matchmap/gia_rotation.py

- Path Execution System
  type: subsystem
  purpose: Explain how automated navigation along predefined paths works.
  answers:
    - How are paths defined and loaded?
    - How does the executor move the character?
    - What are waypoints and target points?
    - How is stuck/timeout detection handled?
  source_hints:
    - myexecutor/BasePathExecutor2.py
    - myexecutor/CordinateTransfer.py
  children:
    - Path Definition
      type: concept
      purpose: Explain the path file format and point types.
      answers:
        - What is the JSON format for path files?
        - What are path points vs target points?
        - What movement modes are available (normal, fly, swim, jump)?
        - What actions can be attached to points?
      source_hints:
        - myexecutor/BasePathExecutor2.py (Point class)
    - Movement Control
      type: concept
      purpose: Explain the real-time movement mechanics during path execution.
      answers:
        - How does small-step approach work near targets?
        - How is direction adjustment performed?
        - How are stuck situations detected and recovered?
        - What happens on position mutation (death teleport)?
      source_hints:
        - myexecutor/BasePathExecutor2.py (move, __do_move methods)
        - controller/BaseController.py
    - Specialized Executors
      type: subsystem
      purpose: Explain the different executor types for specific tasks.
      answers:
        - What executors exist for different automation types?
        - How do CollectPathExecutor, FightPathExecutor differ?
        - What task-specific logic does each executor add?
      source_hints:
        - myexecutor/CollectPathExecutor.py
        - myexecutor/FightPathExecutor.py
        - myexecutor/DailyMissionPathExecutor.py
        - myexecutor/LeyLineOutcropPathExecutor.py
        - myexecutor/DomainController.py

- Combat System
  type: subsystem
  purpose: Explain the automated fighting capabilities and team management.
  answers:
    - How is combat automation implemented?
    - How are fight teams defined and executed?
    - What combat actions are available?
    - How is character death handled?
  source_hints:
    - controller/FightController.py
    - fightmapper/BaseFightMapper.py
    - fightmapper/FightMapperImpl.py
    - server/service/FightTeamService.py
  children:
    - Fight Actions
      type: api
      purpose: Document the available combat action commands.
      answers:
        - What actions can be scripted (skill, burst, attack, charge)?
        - How are movement actions integrated with combat?
        - How is team switching handled?
      source_hints:
        - fightmapper/BaseFightMapper.py (method documentation)
    - Team Configuration
      type: configuration
      purpose: Explain how fight teams are defined and managed.
      answers:
        - How are team files structured?
        - How is team order mapped to in-game slots?
        - How are teams selected for different tasks?
      source_hints:
        - server/service/FightTeamService.py
        - config-template.yaml (default_fight_team)

- Task Automation
  type: subsystem
  purpose: Explain the high-level task automation capabilities.
  answers:
    - What automation tasks are supported?
    - How are daily missions automated?
    - How are ley line challenges handled?
    - How is domain looping implemented?
  source_hints:
    - server/service/DailyMissionService.py
    - server/service/LeyLineOutcropService.py
    - server/service/DomainService.py
    - server/service/OneDragonService.py
  children:
    - Daily Mission Automation
      type: workflow
      purpose: Explain the daily commission automation flow.
      answers:
        - How does the system detect and complete daily missions?
        - What mission types are supported?
        - How is the Katheryne reward claim handled?
      source_hints:
        - myexecutor/DailyMissionPathExecutor.py
        - server/service/DailyMissionService.py
    - Ley Line Automation
      type: workflow
      purpose: Explain ley line challenge automation.
      answers:
        - How are ley lines located and completed?
        - What happens after completing a ley line?
        - How is reward claiming handled?
      source_hints:
        - myexecutor/LeyLineOutcropPathExecutor.py
        - server/service/LeyLineOutcropService.py
    - Domain Looping
      type: workflow
      purpose: Explain domain/abyss automation.
      answers:
        - How does domain looping work?
        - How are domain-specific teams configured?
        - How is the weekly schedule managed?
      source_hints:
        - controller/DomainController.py
        - server/service/DomainService.py
        - config-template.yaml (domain_week_plain)

- Input Control System
  type: subsystem
  purpose: Explain how keyboard and mouse input is automated.
  answers:
    - How are keyboard inputs simulated?
    - How are mouse movements and clicks controlled?
    - How is camera rotation adjusted?
    - How is input gated to active game window?
  source_hints:
    - controller/BaseController.py
    - controller/UIController.py
    - controller/MapController2.py
  children:
    - Keyboard Control
      type: concept
      purpose: Explain keyboard input simulation mechanisms.
      answers:
        - How are key presses/releases simulated?
        - How are movement keys (WASD) managed?
        - How are skill keys (E, Q) handled?
      source_hints:
        - controller/BaseController.py (kb_press, kb_release methods)
    - Mouse Control
      type: concept
      purpose: Explain mouse input simulation and camera control.
      answers:
        - How are mouse clicks simulated?
        - How is camera rotation via mouse movement achieved?
        - How is scroll wheel used for zoom?
      source_hints:
        - controller/BaseController.py (MouseController, camera_chage)
    - UI Interaction
      type: workflow
      purpose: Explain how in-game UI is navigated programmatically.
      answers:
        - How are menus opened and closed?
        - How is teleportation via map UI performed?
        - How are buttons detected and clicked?
      source_hints:
        - controller/MapController2.py
        - controller/UIController.py
        - controller/DialogController.py

- OCR System
  type: subsystem
  purpose: Explain the text recognition capabilities using PaddleOCR.
  answers:
    - How is OCR integrated into the system?
    - What text is recognized in-game?
    - How are OCR results used for automation decisions?
    - How is fight team name detected?
  source_hints:
    - controller/OCRController.py
    - server/service/OCRService.py
    - resources/ocr/
  children:
    - OCR Integration
      type: concept
      purpose: Explain the PaddleOCR integration and usage patterns.
      answers:
        - How is PaddleOCR initialized and used?
        - What screen regions are OCR'd?
        - How is OCR performance optimized?
      source_hints:
        - server/service/OCRService.py
        - controller/OCRController.py

- Configuration System
  type: subsystem
  purpose: Explain the configuration management and options.
  answers:
    - What configuration files exist?
    - How are settings structured and validated?
    - What can be customized?
    - How are path executor parameters tuned?
  source_hints:
    - myutils/configutils.py
    - config-template.yaml
    - config.map.yaml
  children:
    - Server Configuration
      type: configuration
      purpose: Document server and connection settings.
      answers:
        - What server settings are available?
        - How is host/port configured?
        - How is debug mode toggled?
      source_hints:
        - myutils/configutils.py (ServerConfig)
        - config-template.yaml (服务器配置)
    - Path Executor Configuration
      type: configuration
      purpose: Document the path execution tuning parameters.
      answers:
        - What movement parameters can be tuned?
        - How are timeouts configured?
        - How are stuck thresholds adjusted?
      source_hints:
        - myutils/configutils.py (PathExecutorConfig)
        - config-template.yaml (路径执行器配置)
    - Fight Configuration
      type: configuration
      purpose: Document combat-related settings.
      answers:
        - How are fight teams selected?
        - How are fight durations set?
        - How are domain teams mapped?
      source_hints:
        - myutils/configutils.py (FightConfig)
        - config-template.yaml (战斗配置, 秘境配置)

- Utilities Layer
  type: subsystem
  purpose: Explain the supporting utility modules.
  answers:
    - What utility helpers exist?
    - How is file management handled?
    - How are images processed?
    - How are timers and rate limiters used?
  source_hints:
    - myutils/
  children:
    - Image Utilities
      type: reference
      purpose: Document image processing helper functions.
      answers:
        - What image manipulation utilities exist?
        - How is template matching implemented?
        - How are SIFT features processed?
      source_hints:
        - myutils/imgutils.py
        - myutils/template_match_utils.py
        - myutils/sift_utils.py
    - Execution Utilities
      type: reference
      purpose: Document path execution helper functions.
      answers:
        - How is proximity calculated?
        - How are angles computed?
        - How is coordinate transformation handled?
      source_hints:
        - myutils/executor_utils.py
        - myexecutor/CordinateTransfer.py
    - Timing Utilities
      type: reference
      purpose: Document rate limiting and timing helpers.
      answers:
        - How are rate limiters implemented?
        - How are intervals enforced?
      source_hints:
        - myutils/timerutils.py

- API Reference
  type: api
  purpose: Document the REST API endpoints available for external integration.
  answers:
    - What API endpoints are available?
    - How are tasks triggered via API?
    - What data formats are used?
  source_hints:
    - server/controller/*.py
    - server/dto/DataClass.py
  children:
    - Minimap API
      type: api
      purpose: Document minimap-related endpoints.
      answers:
        - How is position retrieved?
        - How is map data accessed?
        - How is rotation queried?
      source_hints:
        - server/controller/MiniMapController.py
    - Task API
      type: api
      purpose: Document task execution endpoints.
      answers:
        - How are paths executed?
        - How are daily missions triggered?
        - How are domains started?
      source_hints:
        - server/controller/TodoController.py
        - server/controller/DailyMissionController.py
        - server/controller/ServerDomainController.py
    - Configuration API
      type: api
      purpose: Document configuration management endpoints.
      answers:
        - How is configuration read/updated?
        - How are files managed?
      source_hints:
        - server/controller/ConfigController.py
        - server/controller/FileManagerController.py

- Development Guide
  type: development
  purpose: Guide developers who want to extend or modify Minimap.
  answers:
    - How do I set up the development environment?
    - How do I add new executors?
    - How do I create new path files?
    - How do I debug issues?
  source_hints:
    - README.md (方式2：从源码安装)
    - myexecutor/PathRecorderManually.py
  children:
    - Adding New Executors
      type: workflow
      purpose: Explain how to create specialized path executors.
      answers:
        - How do I subclass BasePathExecutor?
        - What lifecycle methods should I override?
        - How do I add task-specific logic?
      source_hints:
        - myexecutor/BasePathExecutor2.py
        - myexecutor/CollectPathExecutor.py
    - Creating Path Files
      type: workflow
      purpose: Explain how to create and record new navigation paths.
      answers:
        - How do I use PathRecorderManually?
        - How do I structure path JSON files?
        - How do I add waypoints and targets?
      source_hints:
        - myexecutor/PathRecorderManually.py
        - myexecutor/KeyPointViewer.py
    - Debugging
      type: workflow
      purpose: Explain debugging techniques and tools.
      answers:
        - How do I enable debug mode?
        - How do I view path visualization?
        - How do I interpret logs?
      source_hints:
        - mylogger/MyLogger3.py
        - myexecutor/KeyPointViewer.py
        - config-template.yaml (debug_enable)

- Extension Points
  type: extension
  purpose: Identify where the system can be extended or customized.
  answers:
    - Where can I add new automation tasks?
    - How can I customize fight scripts?
    - How can I integrate new recognition methods?
    - How can I add new API endpoints?
  source_hints:
    - myexecutor/BasePathExecutor2.py
    - fightmapper/FightMapperImpl.py
    - server/controller/*.py
  children:
    - Custom Fight Scripts
      type: extension
      purpose: Explain how to create custom combat sequences.
      answers:
        - How do I create team-specific fight scripts?
        - What action syntax is available?
        - How do I register new teams?
      source_hints:
        - fightmapper/BaseFightMapper.py
        - fightmapper/FightMapperImpl.py
    - Custom Executors
      type: extension
      purpose: Explain how to create task-specific path executors.
      answers:
        - What base class should I extend?
        - What methods should I implement?
        - How do I integrate with the task system?
      source_hints:
        - myexecutor/BasePathExecutor2.py
    - New API Endpoints
      type: extension
      purpose: Explain how to add new REST endpoints.
      answers:
        - How do I create a new controller blueprint?
        - How do I register it with the server?
        - What service patterns should I follow?
      source_hints:
        - server/controller/ServerBaseController.py
        - server/MiniMapServer.py

- Related Projects
  type: reference
  purpose: Document the ecosystem of related repositories.
  answers:
    - What related projects exist in the ecosystem?
    - How does minimap-gui relate to this system?
    - How are path files and map data shared?
  source_hints:
    - README.md (关联仓库)
    - .gitmodules