/**
 * @namespace Interverse
 * @description Type definitions for the Interverse SDK in RPG Maker
 */

/**
 * Item category definitions
 * @enum {string}
 */
export const InterverseItemCategory = {
    WEAPON: "weapon",
    ARMOR: "armor",
    ACCESSORY: "accessory",
    CONSUMABLE: "consumable",
    CURRENCY: "currency",
    COSMETIC: "cosmetic",
    MOUNT: "mount",
    PET: "pet"
} as const;

/**
 * Rarity level definitions
 * @enum {string}
 */
export const InterverseRarity = {
    COMMON: "common",
    UNCOMMON: "uncommon",
    RARE: "rare",
    EPIC: "epic",
    LEGENDARY: "legendary",
    MYTHIC: "mythic"
} as const;

/**
 * Color representation for the blockchain
 * @class
 */
export class InterverseColor {
    /**
     * @constructor
     * @param {number} r - Red component (0-1)
     * @param {number} g - Green component (0-1)
     * @param {number} b - Blue component (0-1)
     * @param {number} a - Alpha component (0-1)
     */
    constructor(
        public r: number = 1.0, 
        public g: number = 1.0, 
        public b: number = 1.0, 
        public a: number = 1.0
    ) {
        // Ensure values are between 0 and 1
        this.r = Math.max(0, Math.min(1, r));
        this.g = Math.max(0, Math.min(1, g));
        this.b = Math.max(0, Math.min(1, b));
        this.a = Math.max(0, Math.min(1, a));
    }

    /**
     * Convert to hexadecimal string
     * @returns {string} Hex color code
     */
    toHex(): string {
        const toHex = (value: number) => {
            const hex = Math.floor(value * 255).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };
        
        return `#${toHex(this.r)}${toHex(this.g)}${toHex(this.b)}`;
    }

    /**
     * Create a color from hex string
     * @param {string} hex - Hex color code
     * @returns {InterverseColor} New color object
     */
    static fromHex(hex: string): InterverseColor {
        hex = hex.replace('#', '');
        if (hex.length === 3) {
            hex = hex.split('').map(c => c + c).join('');
        }
        
        const r = parseInt(hex.slice(0, 2), 16) / 255;
        const g = parseInt(hex.slice(2, 4), 16) / 255;
        const b = parseInt(hex.slice(4, 6), 16) / 255;
        
        return new InterverseColor(r, g, b);
    }
}

/**
 * Represents properties for an asset on the blockchain
 */
export interface InterverseAssetProperties {
    /** Item category */
    category: typeof InterverseItemCategory[keyof typeof InterverseItemCategory];
    
    /** Item rarity */
    rarity: typeof InterverseRarity[keyof typeof InterverseRarity];
    
    /** Item level */
    level: number;
    
    /** Model identifier */
    model_id: string;
    
    /** Primary color */
    primary_color: InterverseColor;
    
    /** Secondary color */
    secondary_color: InterverseColor;
    
    /** Numeric properties */
    numeric_properties: Record<string, number>;
    
    /** String properties */
    string_properties: Record<string, string>;
    
    /** Item tags */
    tags: string[];
}

/**
 * Represents a complete asset on the blockchain
 */
export interface InterverseAsset extends InterverseAssetProperties {
    /** Unique asset identifier */
    asset_id: string;
    
    /** Owner's wallet address */
    owner: string;
}

/**
 * Blockchain-related interfaces
 */
export interface InterverseWallet {
    /** Unique wallet address */
    address: string;
    
    /** Wallet balance */
    balance: number;
    
    /** List of owned assets */
    assets: InterverseAsset[];
}

/**
 * Transaction type definitions
 */
export interface InterverseTransaction {
    /** Unique transaction ID */
    transaction_id: string;
    
    /** Sender's wallet address */
    from: string;
    
    /** Recipient's wallet address */
    to: string;
    
    /** Asset being transferred */
    asset: InterverseAsset;
    
    /** Transaction timestamp */
    timestamp: number;
    
    /** Transaction status */
    status: 'pending' | 'completed' | 'failed';
}

/**
 * Marketplace-related interfaces
 */
export interface InterverseMarketplaceListing {
    /** Unique listing ID */
    listing_id: string;
    
    /** Asset being listed */
    asset: InterverseAsset;
    
    /** Seller's wallet address */
    seller: string;
    
    /** Listing price */
    price: number;
    
    /** Listing status */
    status: 'active' | 'sold' | 'cancelled';
    
    /** Listing timestamp */
    timestamp: number;
}

/**
 * Utility types for type checking and validation
 */
export type InterverseItemCategoryType = typeof InterverseItemCategory[keyof typeof InterverseItemCategory];
export type InterverseRarityType = typeof InterverseRarity[keyof typeof InterverseRarity];

/**
 * Validation functions
 */
export const InterverseValidation = {
    /**
     * Validate item category
     * @param category - Category to validate
     * @returns {boolean} Whether the category is valid
     */
    isValidCategory: (category: string): category is InterverseItemCategoryType => 
        Object.values(InterverseItemCategory).includes(category as InterverseItemCategoryType),

    /**
     * Validate rarity
     * @param rarity - Rarity to validate
     * @returns {boolean} Whether the rarity is valid
     */
    isValidRarity: (rarity: string): rarity is InterverseRarityType => 
        Object.values(InterverseRarity).includes(rarity as InterverseRarityType),

    /**
     * Validate asset
     * @param asset - Asset to validate
     * @returns {boolean} Whether the asset is valid
     */
    isValidAsset: (asset: Partial<InterverseAsset>): asset is InterverseAsset => {
        if (!asset.asset_id || !asset.owner) return false;
        return this.isValidCategory(asset.category) && 
               this.isValidRarity(asset.rarity);
    }
};

export default {
    ItemCategory: InterverseItemCategory,
    Rarity: InterverseRarity,
    Color: InterverseColor,
    Validation: InterverseValidation
};