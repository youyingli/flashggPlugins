#ifndef __PDFWEIGHTPRODUCER__
#define __PDFWEIGHTPRODUCER__

#include "flashgg/DataFormats/interface/PDFWeightObject.h"

#include "flashggPlugins/flashggAnalysisNtuplizer/interface/DataFormats.h"

namespace flashggAnalysisNtuplizer {

    void 
    PDFWeightsProducer (std::vector<flashgg::PDFWeightObject> PDFWeights, flashggAnalysisTreeFormatStd& dataformat, float genweight) 
    {
        for( unsigned int weight_index = 0; weight_index < PDFWeights.size(); weight_index++ ){
        
            std::vector<float> pdfWeights;
            std::vector<uint16_t> compressed_weights         = PDFWeights[weight_index].pdf_weight_container; 
            std::vector<uint16_t> compressed_alpha_s_weights = PDFWeights[weight_index].alpha_s_container; 
            std::vector<uint16_t> compressed_scale_weights   = PDFWeights[weight_index].qcd_scale_container;
 
            std::vector<float> uncompressed         = PDFWeights[weight_index].uncompress( compressed_weights );
            std::vector<float> uncompressed_alpha_s = PDFWeights[weight_index].uncompress( compressed_alpha_s_weights );
            std::vector<float> uncompressed_scale   = PDFWeights[weight_index].uncompress( compressed_scale_weights );
        
            for( unsigned int j=0; j<PDFWeights[weight_index].pdf_weight_container.size();j++ ) {
                dataformat.pdf_Weights.push_back(uncompressed[j]/genweight);
                                    //std::cout << "pdfWeights " << j<< " " << uncompressed[j] << std::endl;
            }
            for( unsigned int j=0; j<PDFWeights[weight_index].alpha_s_container.size();j++ ) {
                dataformat.alphas_Weights.push_back(uncompressed_alpha_s[j]/genweight);
                                    //std::cout << "alpha_s " << j << " " << uncompressed_alpha_s[j] << std::endl;
            }
            for( unsigned int j=0; j<PDFWeights[weight_index].qcd_scale_container.size();j++ ) {
                dataformat.qcdScale_Weights.push_back(uncompressed_scale[j]/genweight);
            }
        }

    }

}

#endif
