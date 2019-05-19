graph TD
    A --> X["Database"];
    A["TCPServer"];
    B["Mobile App"]-->A;
    C["Flask Admin"]-->A;
    D["Interface"]-->C;
    K["BuyNode"]-->B;

