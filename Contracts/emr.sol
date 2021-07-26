pragma solidity >=0.4.16;
contract emr{
    struct emr_id{
        string id;
    }
    emr_id[] public emr_records;

    function add(string memory _id) public returns (string memory) {
        emr_records.push(emr_id(_id));
        return _id;
    }

    function search(string memory name1) public view returns(bool) {
        for (uint i = 0; i < emr_records.length+1; i++){
            if(keccak256(abi.encodePacked(emr_records[i].id)) == keccak256(abi.encodePacked(name1))){
                return true;
            }
        }
        return false;
    }
    function deleter(string memory name1) public returns(bool) {
        for (uint i = 0; i < emr_records.length+1; i++){
            if(keccak256(abi.encodePacked(emr_records[i].id)) == keccak256(abi.encodePacked(name1))){
                delete emr_records[i];
                return true;
            }
        }
        return false;
    }
}
