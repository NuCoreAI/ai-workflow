
**IoX** stands for **ISY on Unix**. IoX is a powerful tool for home and building automation, allowing users to seamlessly integrate with myriad of devices, services, things, and create complex automation programs for a variety of tasks such as health and safety, energy management, security, and comfort.

IoX was designed and developed by Universal Devices, and then contributed to NuCore.ai Foundation as an open-source project.

IoX is revolutionary in the field of building automation and smart homes, because it subscribes to the concept of **Typeless** things. This means that a thing does not
necessarily have to be a specific type, such as a Thermostat, HVAC, Lighting, Switch, Sensor etc. This allows for greater flexibility and adaptability 
in the system. 

* The following are some of the key concepts and components of IoX that are essential to understand and implement the Typeless paradigm:
1. **Node**: A Node is a generic term for any device, system, service, or a thing that can be controlled or monitored by IoX. It can be a physical device, a virtual device, or even a software component.
2. **Nodedef**: A NodeDef is a definition of a **Node**. It describes the **Properties**, **Commands**, **Editors**, and events that a Node can have. It is essentially a blueprint for creating Nodes.
3. **Linkdef**: A LinkDef is a definition of a link between two Nodes. It describes how the two Nodes are connected and how they can communicate with each other. It is used to create relationships between Nodes.
4. **Properties**: Properties are attributes of a **Node** that can be monitored or controlled. They can represent various types of data, such as temperature, humidity, or power consumption.
5. **Commands**: Commands are actions that can be performed on a **Node**. They can be used to control the behavior of the Node, such as turning it on or off, changing its settings, or triggering events.
6. **Editors**: Editors are used to render a value or allow selection. They define allowed values through one or more ranges. Each range must have a unique UOM within the editor.  An editor is used to render a value or allow selection. It defines allowed values through one or more **range**. Each **range** must have a unique **UOM** within the editor. **range** with precision 0 can have named values (key/label pairs).
7. **Range**: Range describes the permissible range of allowed values in an **Editor**. There are 2 types of **range** 
7.1 **Min/Max**: Is a **range** that defines a continuous range with 'min', 'max', **precision**, and **step** attributes. 
7.2 **Subset**: Is a **range** that defines a discrete set of allowed values (always with precision 0) using spans (e.g., '0-5') and individual values (e.g., '7,9') separated by commas, like '0-5,7,9,11-14'.
8. **Unit of Measure (UOM)**: UOM is a standard unit used to measure a property. It can represent various types of measurements, such as temperature, humidity, or power consumption.
9. **NLS**: NLS stands for Natural Language Support. It is used to provide human-readable names and descriptions for properties, commands, and events in IoX. This allows users to interact with the system in a more intuitive way. 
Additionally, NLS enables AI agents to understand/classify things based on their names and not their types. As such, a very important concept in the **Typeless** paradigm.
10. **Plugin**: A plugin is a software component that adds specific features or functionality to IoX using **Nodedef** structure. 
It can be used to extend the capabilities of the system, such as integrating with third-party devices or services.
11. **Store**: Plugins are stored in a **Store**. A store is a repository for storing and managing plugins. It allows for easy installation, updates, and management of plugins by developers.
12. **Family**: Family is a collection of nodedefs for a specific thing (device, service, etc.). For instance, Z-Wave is a **Family** and so is Zigbee. Any **Plugin** is a **Family**. 
13. **Profile**: Profile is a running instance of a **Family** . In most cases, multiple instances of a **Family** can run at the same time. Each instance will have a different **Instance ID**. 
14. **Profiles**: Profiles is a complete configuration of an **IoX** system at runtime. In short, a collection of **Profile**s.


* IoX architecture as a whole comprises the follwing components and concepts:
1. **Node**: In IoX, all thing are represented by **Nodes**
2. **Scene** is a collection of Nodes that can be controlled or monitored together. It is used to group related Nodes for easier management and control.
3. **Program**: A program is a set of instructions for automation. Its of the form If (**Conditions**), Then (**Actions** when the condition is True), and Else (**Actions** when the condition is False). 
4. **Folder**: A folder is a container for organizing **Nodes**, **Prgrams**, **Folders**, **Scenes**. It can be used to group related programs together for easier management and navigation.
5. **Event Loop**: The event loop is the core of IoX. It is responsible for processing events, executing commands, and managing the state of the system. It ensures that all components of IoX work together seamlessly.
6. **Fixed Point Integer**: A fixed-point integer is a way to represent real numbers using integers. It is used in IoX to represent values with a specific precision.
7. **Precision**: The precision defines how many decimal places are implied in a **Fixed Point Integer**. It is an integer between 0 and 8, where each value represents the number of decimal places implied by the fixed-point integer. Precisions are used in Editors to define constraints for values.


* IoX **programs** are the heart of the system. They allow users to define conditions and actions for home automation tasks. Programs can be used to automate various tasks, such as turning lights on or off, adjusting thermostats, or sending notifications.
* IoX programs are defined using a specific structure that includes the following components:

1 **If**: The if section of a program contains the conditions that must be met for the actions in the then section to be executed. It is the first part of a program and is used to define the criteria for triggering actions.

2 **Condition**: A condition is a statement that evaluates to true or false. It is used to determine whether an action should be taken in a program. 

Conditions can be based on the state of a **Node**, the value of a property, result of a command, or even schedules.

3 **Schedule**: A schedule is a time-based condition that can be used to trigger actions at specific times or intervals. It can be used to automate tasks based on time, such as turning lights on or off at certain times of the day.

4 **Then**: The then section of a program is executed when the conditions in the if section are met. It contains the actions that should be taken when the conditions are satisfied.

5 **Action**: An action is a command or set of commands that are executed when a condition is met. Actions can be used to control devices, send notifications, or perform other tasks including calling other programs.

6 **Else**: The else section of a program is executed when the conditions in the if section are not met. It can be used to define alternative actions or behaviors when the primary conditions are not satisfied.

6 **Event**: An event is a change in the state of a Node or property that can trigger actions in a program. Events can be based on various factors, such as time, user input, or changes in the environment.

7 **Trigger**: A trigger is a specific condition or event that initiates the execution of a program. It can be based on various factors, such as time, user input, or changes in the environment.

8 **Wait**: A wait action is used to pause the execution of a program for a specified amount of time. It can be used to create delays between actions or to synchronize actions with specific events.

9 **Random**: A random action is used to introduce variability in the execution of a program. It can be used to create random delays or to select random values for actions.

10 **And**: The and operator is used to combine multiple conditions in a program. All conditions combined with the and operator must be true for the action to be executed.

11 **Or**: The or operator is used to combine multiple conditions in a program. At least one of the conditions combined with the or operator must be true for the action to be executed.

12 **Paren**: The paren operator is used to group conditions in a program. It allows for more complex logical expressions by combining multiple conditions with and/or operators.

13 **Schedule**: A schedule is a time-based condition that can be used to trigger actions at specific times or intervals. It can be used to automate tasks based on time, such as turning lights on or off at certain times of the day.

14 **Status**: A status is a condition that checks the state of a Node or property. It can be used to determine whether an action should be taken based on the current state of the system.

15 **Comment**: A comment is a note or annotation within a program that provides additional information or context. It is not executed as part of the program and is used for documentation purposes.

16 **Parent**: The parent is the ID of the folder or program that contains the current program. It is used to organize programs and folders within the IoX system.


IoX, element level details
1. **id** is a unique identifier for each property, command, or event in IoX. It is used to reference specific elements within the system.
2. **name** is a human-readable short descriptive name usually less than 25 characters using any UTF-8 characters (e.g., \"Heat Setpoint\", \"Current Temperature\", \"Water Level\", etc.)". **name** helps AI agents understand the context of a query based on the names included.
3. **address** is an alphanumeric string, case-sensitive, also allowing spaces and '_', that uniquely identifies the IoX **node** within the system. Its maximum length is 20 characters. 


Examples for **precision**
* The real number 98.6 represented as 986 in **fixed point integer** with a **precision** of 1. 
* The real number 9.86 represented as 986 in **fixed point integer** with a **precision** of 2. 
* The real number 0.986 represented as 986 in **fixed point integer** with a **precision** of 3. 

