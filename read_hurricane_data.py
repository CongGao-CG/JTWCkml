import pandas as pd
from datetime import datetime
import re

def read_hurricane_data(filepath, hurricane_only=True):
    """
    Read a HURDAT2 format hurricane track file and return as pandas DataFrame.
    
    Parameters:
    filepath (str): Path to the .txt file containing hurricane data
    hurricane_only (bool): If True, only return basic hurricane data (default).
                          If False, include extended data fields as data-15 to data+15
    
    Returns:
    pandas.DataFrame: DataFrame with columns [time, status, lat, lon, wind, pressure]
                     and optionally data-15 through data+15 if hurricane_only=False
    """
    
    def parse_coordinate(coord_str):
        """Parse coordinate string like '27.4N' or '87.7W' to float with proper sign"""
        if not coord_str or coord_str.strip() == '':
            return None
        
        # Extract number and direction
        match = re.match(r'([0-9.]+)([NSEW])', coord_str.strip())
        if not match:
            return None
        
        value = float(match.group(1))
        direction = match.group(2)
        
        # Apply sign based on direction
        if direction in ['S', 'W']:
            value = -value
            
        return value
    
    def parse_datetime(date_str, time_str):
        """Parse date (YYYYMMDD) and time (HHMM) strings to datetime"""
        try:
            date_str = date_str.strip()
            time_str = time_str.strip()
            
            # Handle cases where time might be missing or malformed
            if len(time_str) != 4:
                time_str = '0000'
                
            datetime_str = f"{date_str}{time_str}"
            return datetime.strptime(datetime_str, '%Y%m%d%H%M')
        except:
            return None
    
    data_rows = []
    
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    # Skip the header line (first line with storm info)
    for line in lines[1:]:
        if line.strip() == '':
            continue
            
        # Split the line by comma and clean whitespace
        parts = [part.strip() for part in line.split(',')]
        
        if len(parts) < 8:  # Need at least 8 fields for basic data
            continue
        
        try:
            # Extract required fields
            date = parts[0]
            time = parts[1]
            record_id = parts[2]  # Sometimes 'L' for landfall, usually blank
            status = parts[3]
            lat_str = parts[4]
            lon_str = parts[5]
            wind = parts[6]
            pressure = parts[7]
            
            # Parse datetime
            parsed_time = parse_datetime(date, time)
            if parsed_time is None:
                continue
            
            # Parse coordinates
            lat = parse_coordinate(lat_str)
            lon = parse_coordinate(lon_str)
            
            # Parse wind and pressure (handle -999 as missing)
            try:
                wind_val = int(wind) if wind != '-999' else None
            except:
                wind_val = None
                
            try:
                pressure_val = int(pressure) if pressure != '-999' else None
            except:
                pressure_val = None
            
            # Create row dictionary with basic data
            row_data = {
                'time': parsed_time,
                'status': status,
                'lat': lat,
                'lon': lon,
                'wind': wind_val,
                'pressure': pressure_val
            }
            
            # If hurricane_only is False, add extended data fields
            if not hurricane_only and len(parts) == 52:
                # Get the last 31 fields (data-15 to data+15)
                extended_data = parts[-31:]
                
                # Add each field as data-15 through data+15
                for i, value in enumerate(extended_data):
                    col_name = f'data{i-15:+d}'  # Format as data-15, data-14, ..., data+0, ..., data+15
                    row_data[col_name] = float(value)
 
            # Add to data if we have minimum required fields
            if lat is not None and lon is not None:
                data_rows.append(row_data)
                
        except Exception as e:
            # Skip malformed lines
            print(f"Warning: Skipping malformed line: {line.strip()}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Sort by time to ensure chronological order
    if not df.empty:
        df = df.sort_values('time').reset_index(drop=True)
    
    return df

# Example usage:
if __name__ == "__main__":
    # Example of how to use the function
    
    # Basic usage (hurricane data only)
    # df = read_hurricane_data('AL122003_HENRI_22.txt')
    # print(df.head())
    # print(f"Shape: {df.shape}")
    # print(f"Columns: {df.columns.tolist()}")
    
    # Extended usage (include all data fields)
    # df_extended = read_hurricane_data('AL122003_HENRI_22.txt', hurricane_only=False)
    # print(df_extended.head())
    # print(f"Shape: {df_extended.shape}")
    # print(f"Columns: {df_extended.columns.tolist()}")
    pass
