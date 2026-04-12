// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ModelRegistry {
    struct ModelRecord {
        bytes32 contentHash;
        string modelSlug;
        string licenseType;
        address registrant;
        uint256 registeredAt;
        uint256 version;
    }

    mapping(bytes32 => ModelRecord) public models;
    mapping(string => bytes32[]) public slugVersions;

    event ModelRegistered(
        bytes32 indexed contentHash,
        string modelSlug,
        string licenseType,
        address indexed registrant,
        uint256 version
    );

    function registerModel(
        bytes32 contentHash,
        string calldata modelSlug,
        string calldata licenseType
    ) external {
        require(models[contentHash].registeredAt == 0, "Already registered");

        uint256 ver = slugVersions[modelSlug].length + 1;

        models[contentHash] = ModelRecord({
            contentHash: contentHash,
            modelSlug: modelSlug,
            licenseType: licenseType,
            registrant: msg.sender,
            registeredAt: block.timestamp,
            version: ver
        });

        slugVersions[modelSlug].push(contentHash);

        emit ModelRegistered(contentHash, modelSlug, licenseType, msg.sender, ver);
    }

    function verifyModel(
        bytes32 contentHash
    )
        external
        view
        returns (
            string memory modelSlug,
            string memory licenseType,
            address registrant,
            uint256 registeredAt,
            uint256 version
        )
    {
        ModelRecord memory r = models[contentHash];
        require(r.registeredAt > 0, "Not registered");
        return (r.modelSlug, r.licenseType, r.registrant, r.registeredAt, r.version);
    }

    function getVersionCount(string calldata modelSlug) external view returns (uint256) {
        return slugVersions[modelSlug].length;
    }

    function getVersionHash(
        string calldata modelSlug,
        uint256 index
    ) external view returns (bytes32) {
        require(index < slugVersions[modelSlug].length, "Index out of bounds");
        return slugVersions[modelSlug][index];
    }
}
